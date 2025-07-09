from flask import Flask, render_template, request, jsonify
import openrouteservice
from openrouteservice.distance_matrix import distance_matrix
import folium
import os
from dotenv import load_dotenv
import numpy as np
from itertools import permutations
import math

app = Flask(__name__)

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

print("API KEY:", ORS_API_KEY)
client = openrouteservice.Client(key=ORS_API_KEY)

# A fixed focus point near Koramangala, Bangalore
focus_lat, focus_lon = 12.9352, 77.6146

def calculate_route_distance(route_indices, distance_matrix):
    """Calculate total distance for a route"""
    total_distance = 0
    for i in range(len(route_indices) - 1):
        total_distance += distance_matrix[route_indices[i]][route_indices[i + 1]]
    return total_distance

def calculate_route_score_with_priority(route_indices, items, distance_matrix):
    """Calculate route score considering distance and perishable item priority"""
    total_distance = calculate_route_distance(route_indices, distance_matrix)
    
    # Priority penalty for perishable items delivered later
    priority_penalty = 0
    for i in range(1, len(route_indices)):  # Skip starting position
        if items[route_indices[i]]['type'] == 'perishable':
            # Heavy penalty for each position a perishable item is delayed
            # Penalty increases exponentially with position
            priority_penalty += (i - 1) * 5.0  # 5km penalty per position
    
    return total_distance + priority_penalty

def two_opt_improvement(route_indices, distance_matrix):
    """Apply 2-opt local search improvement to the route"""
    improved = True
    best_route = route_indices[:]
    best_distance = calculate_route_distance(best_route, distance_matrix)
    
    while improved:
        improved = False
        for i in range(1, len(route_indices) - 1):
            for j in range(i + 1, len(route_indices)):
                # Create new route by reversing the segment between i and j
                new_route = route_indices[:]
                new_route[i:j+1] = reversed(new_route[i:j+1])
                
                new_distance = calculate_route_distance(new_route, distance_matrix)
                
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    break
            if improved:
                break
        route_indices = best_route
    
    return best_route

def nearest_neighbor_with_priority(coords, items, distance_matrix):
    """Improved nearest neighbor algorithm with priority consideration"""
    n = len(coords)
    if n <= 1:
        return list(range(n))
    
    # Start from current location (index 0)
    current_pos = 0
    unvisited = set(range(1, n))
    route = [current_pos]
    
    # Separate items by type for priority handling
    perishable_items = {i for i in range(1, n) if items[i]['type'] == 'perishable'}
    
    while unvisited:
        best_next = None
        best_score = float('inf')
        
        for next_pos in unvisited:
            distance = distance_matrix[current_pos][next_pos]
            
            # Base score is distance
            score = distance
            
            # Strong priority bonus for perishable items
            if next_pos in perishable_items:
                # Higher priority if we still have many perishable items to deliver
                remaining_perishable = len(perishable_items & unvisited)
                priority_bonus = -10.0 * remaining_perishable  # Strong negative bonus
                score += priority_bonus
            
            # Penalty for non-perishable items if perishable items are still pending
            elif perishable_items & unvisited:
                score += 15.0  # Penalty for choosing non-perishable when perishable are waiting
            
            if score < best_score:
                best_score = score
                best_next = next_pos
        
        route.append(best_next)
        unvisited.remove(best_next)
        current_pos = best_next
    
    return route

def optimize_delivery_route_advanced(coords, items, distance_matrix):
    """Advanced route optimization with multiple strategies"""
    n = len(coords)
    if n <= 1:
        return list(range(n))
    
    best_route = None
    best_score = float('inf')
    
    # Strategy 1: Try all permutations for small problems
    if n <= 8:
        print(f"Using exhaustive search for {n} locations")
        for perm in permutations(range(1, n)):
            route = [0] + list(perm)
            score = calculate_route_score_with_priority(route, items, distance_matrix)
            if score < best_score:
                best_score = score
                best_route = route
    
    # Strategy 2: Multiple greedy attempts with different starting strategies
    else:
        print(f"Using heuristic approach for {n} locations")
        
        # Attempt 1: Priority-based nearest neighbor
        route1 = nearest_neighbor_with_priority(coords, items, distance_matrix)
        score1 = calculate_route_score_with_priority(route1, items, distance_matrix)
        
        if score1 < best_score:
            best_score = score1
            best_route = route1
        
        # Attempt 2: Perishable items first, then optimize
        perishable_indices = [i for i in range(1, n) if items[i]['type'] == 'perishable']
        non_perishable_indices = [i for i in range(1, n) if items[i]['type'] == 'non-perishable']
        
        # Sort perishable items by distance from start
        perishable_indices.sort(key=lambda x: distance_matrix[0][x])
        # Sort non-perishable items by distance from start
        non_perishable_indices.sort(key=lambda x: distance_matrix[0][x])
        
        route2 = [0] + perishable_indices + non_perishable_indices
        score2 = calculate_route_score_with_priority(route2, items, distance_matrix)
        
        if score2 < best_score:
            best_score = score2
            best_route = route2
        
        # Attempt 3: Nearest neighbor without priority, then 2-opt
        route3 = nearest_neighbor_basic(coords, distance_matrix)
        route3 = two_opt_improvement(route3, distance_matrix)
        score3 = calculate_route_score_with_priority(route3, items, distance_matrix)
        
        if score3 < best_score:
            best_score = score3
            best_route = route3
    
    # Apply 2-opt improvement to the best route found
    if best_route and n > 3:
        best_route = two_opt_improvement(best_route, distance_matrix)
    
    print(f"Best route found with score: {best_score}")
    return best_route

def nearest_neighbor_basic(coords, distance_matrix):
    """Basic nearest neighbor algorithm focusing only on distance"""
    n = len(coords)
    if n <= 1:
        return list(range(n))
    
    current_pos = 0
    unvisited = set(range(1, n))
    route = [current_pos]
    
    while unvisited:
        nearest = min(unvisited, key=lambda x: distance_matrix[current_pos][x])
        route.append(nearest)
        unvisited.remove(nearest)
        current_pos = nearest
    
    return route

def analyze_route_quality(route_indices, items, distance_matrix):
    """Analyze the quality of a route"""
    total_distance = calculate_route_distance(route_indices, distance_matrix)
    
    # Check perishable item positions
    perishable_positions = []
    for i, idx in enumerate(route_indices):
        if idx > 0 and items[idx]['type'] == 'perishable':
            perishable_positions.append(i)
    
    # Calculate average position of perishable items
    avg_perishable_position = sum(perishable_positions) / len(perishable_positions) if perishable_positions else 0
    
    return {
        'total_distance': total_distance,
        'perishable_positions': perishable_positions,
        'avg_perishable_position': avg_perishable_position,
        'perishable_delivered_early': sum(1 for p in perishable_positions if p <= len(route_indices) // 2)
    }

def geocode_address(address):
    """Geocode an address with better error handling using the working API endpoint"""
    try:
        print(f"🔍 Geocoding: {address}")
        
        # Add ", India" to the address for better results
        search_address = f"{address}, India" if ", India" not in address else address
        
        # Use the working API endpoint
        res = client.request(
            '/geocode/search',
            {
                'text': search_address,
                'size': 1,
                'focus.point.lat': focus_lat,
                'focus.point.lon': focus_lon,
                'boundary.country': 'IN'
            }
        )
        
        print(f"📍 API Response for '{address}': {res}")
        
        features = res.get('features', [])
        if not features:
            print(f"❌ No features found for '{address}'")
            return None
        
        feature = features[0]
        geometry = feature.get('geometry', {})
        coordinates = geometry.get('coordinates', [])
        
        if not coordinates or len(coordinates) < 2:
            print(f"❌ Invalid coordinates for '{address}'")
            return None
        
        lon, lat = coordinates[0], coordinates[1]
        
        # Check if coordinates are in Bangalore area (expanded bounds)
        if not (12.5 <= lat <= 13.5 and 77.0 <= lon <= 78.0):
            print(f"⚠️ Coordinates outside Bangalore area: {lat}, {lon}")
            return None
        
        properties = feature.get('properties', {})
        label = properties.get('label', address)
        
        print(f"✅ Successfully geocoded '{address}' to ({lat}, {lon})")
        return {
            'coordinates': (lon, lat),
            'label': label
        }
        
    except Exception as e:
        print(f"❌ Exception geocoding '{address}': {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    optimized_addresses = []
    map_html = None
    error = None
    route_info = None

    if request.method == 'POST':
        current_address = request.form.get('current_address', '').strip()
        addresses = [a.strip() for a in request.form.getlist('address') if a.strip()]
        item_types = request.form.getlist('item_type')

        if not current_address:
            error = "Please enter your current address."
        elif len(addresses) < 1:
            error = "Please enter at least one delivery address."
        else:
            # Combine current address with delivery addresses
            all_addresses = [current_address] + addresses
            all_item_types = ['current'] + item_types[:len(addresses)]
            
            coords = []
            items = []
            geocoded_addresses = []
            failed_addresses = []
            
            for i, addr in enumerate(all_addresses):
                result = geocode_address(addr)
                if result:
                    coords.append(result['coordinates'])
                    geocoded_addresses.append(result['label'])
                    items.append({
                        'address': result['label'],
                        'type': all_item_types[i],
                        'original_index': i
                    })
                else:
                    failed_addresses.append(addr)

            if len(coords) < 2:
                if failed_addresses:
                    error = f"Could not geocode the following addresses: {', '.join(failed_addresses)}. Please check the addresses and try again."
                else:
                    error = "Could not geocode current address and at least one delivery address near Bangalore."
            else:
                try:
                    print(f"📊 Processing {len(coords)} locations")
                    
                    # Get distance matrix
                    matrix = distance_matrix(
                        client,
                        locations=coords,
                        profile='driving-car',
                        metrics=['distance'],
                        resolve_locations=True,
                        units='km'
                    )
                    distances = matrix['distances']
                    
                    print(f"📏 Distance matrix calculated: {len(distances)}x{len(distances[0])}")
                    
                    # Optimize route with advanced algorithm
                    optimized_indices = optimize_delivery_route_advanced(coords, items, distances)
                    
                    # Analyze route quality
                    route_analysis = analyze_route_quality(optimized_indices, items, distances)
                    print(f"🔍 Route Analysis: {route_analysis}")
                    
                    # Prepare results
                    optimized_coords = [coords[i] for i in optimized_indices]
                    optimized_addresses = [items[i]['address'] for i in optimized_indices]
                    optimized_types = [items[i]['type'] for i in optimized_indices]
                    
                    # Calculate route statistics
                    total_distance = route_analysis['total_distance']
                    
                    perishable_count = sum(1 for t in optimized_types if t == 'perishable')
                    non_perishable_count = sum(1 for t in optimized_types if t == 'non-perishable')
                    
                    route_info = {
                        'total_distance': round(total_distance, 2),
                        'total_stops': len(optimized_indices) - 1,  # Excluding current location
                        'perishable_count': perishable_count,
                        'non_perishable_count': non_perishable_count,
                        'perishable_avg_position': round(route_analysis['avg_perishable_position'], 1),
                        'perishable_delivered_early': route_analysis['perishable_delivered_early']
                    }
                    
                    print(f"🎯 Route optimized: {route_info}")
                    
                    # Generate map
                    fmap = folium.Map(location=[focus_lat, focus_lon], zoom_start=13)
                    
                    for idx, (lon, lat) in enumerate(optimized_coords):
                        if idx == 0:
                            # Current location - green marker
                            folium.Marker(
                                [lat, lon], 
                                popup=f"START: {optimized_addresses[idx]}",
                                icon=folium.Icon(color='green', icon='home')
                            ).add_to(fmap)
                        else:
                            # Delivery locations - different colors for different types
                            color = 'red' if optimized_types[idx] == 'perishable' else 'blue'
                            icon = 'exclamation-sign' if optimized_types[idx] == 'perishable' else 'info-sign'
                            
                            folium.Marker(
                                [lat, lon], 
                                popup=f"{idx}. {optimized_addresses[idx]} ({optimized_types[idx].title()})",
                                icon=folium.Icon(color=color, icon=icon)
                            ).add_to(fmap)
                    
                    # Add route line
                    folium.PolyLine(
                        [(lat, lon) for lon, lat in optimized_coords], 
                        color='purple', 
                        weight=3,
                        opacity=0.8
                    ).add_to(fmap)
                    
                    map_html = fmap._repr_html_()
                    
                    # Prepare optimized addresses with types for display
                    optimized_addresses = [
                        {
                            'address': addr,
                            'type': optimized_types[i],
                            'is_current': i == 0
                        }
                        for i, addr in enumerate(optimized_addresses)
                    ]
                    
                    # Show warning if some addresses failed
                    if failed_addresses:
                        print(f"⚠️ Warning: Some addresses could not be geocoded: {failed_addresses}")
                    
                except Exception as e:
                    error = f"Error optimizing route: {e}"
                    print(f"Full error: {str(e)}")
                    import traceback
                    traceback.print_exc()

    return render_template("index.html", 
                         optimized_addresses=optimized_addresses, 
                         map_html=map_html, 
                         error=error,
                         route_info=route_info)

if __name__ == '__main__':
    app.run(debug=True)
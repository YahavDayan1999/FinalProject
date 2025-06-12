import math
import random

venues = []
artists = []
shows = []

historical_shows = [
    {"artist": "Noa Kirel", "genre": "Pop", "venue": "Zappa Tel Aviv", "price": 90 , "date" : "05/09/2025"},
    {"artist": "Omer Adam", "genre": "Mizrahi", "venue": "Zappa Rishon Lezion ", "price": 120 , "date" : "08/10/2025"},
    {"artist": "Eden Hasson", "genre": "Mizrahi", "venue": "Zappa Haifa", "price": 100, "date" : "22/10/2025"},
    {"artist": "Shlomo Artzi", "genre": "Israeli", "venue": "Menora Tel Aviv", "price": 120, "date" : "23/11/2025"},
    {"artist": "Yuval Dayan", "genre": "Israeli", "venue": "Zappa Haifa", "price": 170, "date" : "02/12/2025"},
]


predefined_shows = [
    {"artist_name": "Noa Kirel", "genre": "Pop", "venue_name": "Zappa Tel Aviv", "date": "05/09/2026", "price": 90},
    {"artist_name": "Omer Adam", "genre": "Mizrahi", "venue_name": "Zappa Rishon Lezion", "date": "08/10/2025", "price": 120}
]

for show_data in predefined_shows:

    artist = next((a for a in artists if a["name"] == show_data["artist_name"]), None)
    if not artist:
        artist = {"name": show_data["artist_name"], "genre": show_data["genre"]}
        artists.append(artist)


    venue = next((v for v in venues if v["name"] == show_data["venue_name"]), None)
    if not venue:
        venue = {"name": show_data["venue_name"], "capacity": 400, "rows": 20, "seats_per_row": 20}
        venues.append(venue)


    seats = [['[ ]' for _ in range(venue["seats_per_row"])] for _ in range(venue["rows"])]


    shows.append({
        "venue": venue,
        "artist": artist,
        "date": show_data["date"],
        "base_price": show_data["price"],
        "sold_tickets": 0,
        "seats": seats
    })


def display_historical_shows():
    print("\n📜 Historical Shows (for reference):")
    for i, h in enumerate(historical_shows):
        print(f"{i + 1}. {h['artist']} ({h['genre']}) at {h['venue']} on {h['date']} - Price: ${h['price']}")



clients = {}  # Stores {ID: {"name": name, "real_id": valid_id or system_id}}
purchases = {}  # Stores {client_id: {"name": client_name, "spent": total_amount_spent}}
generated_ids = set()  # Stores system-generated IDs to prevent duplicates


def is_valid_israeli_id(client_id):
    """Validate Israeli ID using checksum method."""
    client_id = str(client_id)  # Ensure it's a string
    if len(client_id) != 9 or not client_id.isdigit():
        return False

    # Calculate checksum
    checksum = sum(
        sum(divmod(int(digit) * (2 if i % 2 else 1), 10))
        for i, digit in enumerate(client_id)
    )
    return checksum % 10 == 0


def generate_system_id():
    """Generate a unique system ID for invalid entries."""
    while True:
        system_id = f"SYS{random.randint(1000, 9999)}"
        if system_id not in generated_ids:
            generated_ids.add(system_id)
            return system_id


def recommend_dynamic_pricing(genre, location, artist_name=None):
    prices = []

    for show in shows:
        if show['artist']['genre'].lower() == genre.lower() and show['venue']['name'].lower() == location.lower():
            price = show['base_price']
            sold = show['sold_tickets']
            cap = show['venue']['capacity']
            demand = (sold / cap) * 100 if cap else 0
            if demand >= 90:
                price *= 1.4
            elif demand >= 75:
                price *= 1.2
            elif demand >= 50:
                price *= 1.1
            prices.append(price)


    for hist in historical_shows:
        if hist["genre"].lower() == genre.lower() and hist["venue"].lower() == location.lower():
            if not artist_name or artist_name.lower() == hist["artist"].lower():
                prices.append(hist["price"])

    if not prices:
        return None, None

    avg = sum(prices) / len(prices)
    return round(avg * 0.9, 2), round(max(prices) * 1.1, 2)


def client_login():
    """Handles client login with ID validation."""
    name = input("Enter your name: ").strip()
    client_id = input("Enter your Israeli ID (or previous system-assigned ID): ").strip()

    if client_id in clients:
        # ID exists, check if the name matches
        if clients[client_id]["name"] == name:
            print(f"Welcome back, {name}!")
            client_menu()
        else:
            print("ID does not match the stored name. Access denied.")
        return

    if is_valid_israeli_id(client_id):
        clients[client_id] = {"name": name, "real_id": client_id}
        print("✅ Valid ID! Registered successfully.")
    else:
        system_id = generate_system_id()
        clients[system_id] = {"name": name, "real_id": system_id}
        print(f"❌ Invalid ID! You have been assigned a system ID: {system_id}")

    client_menu()


def client_menu():
    while True:
        print("\nClient Menu:")
        print("1. Search for Shows")
        print("2. Buy Ticket")
        print("3. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            search_shows()
        elif choice == "2":
            buy_ticket()
        elif choice == "3":
            break
        else:
            print("Invalid choice, please try again.")


def search_shows():
    print("\n🎤 Available Historical Shows:")
    for i, show in enumerate(historical_shows, start=1):
        print(f"{i}. {show['artist']} ({show['genre']}) at {show['venue']} on {show['date']} - Ticket Price: ${show['price']}")



def process_credit_card_payment(amount):
    print(f"\n💳 Payment Required: ${amount:.2f}")
    card_number = input("Enter credit card number (16 digits): ").strip()
    expiry = input("Enter expiry date (MM/YY): ").strip()
    cvv = input("Enter CVV (3 digits): ").strip()

    if not (card_number.isdigit() and len(card_number) == 16):
        print("❌ Invalid card number.")
        return False
    if not (len(expiry) == 5 and expiry[2] == '/' and expiry[:2].isdigit() and expiry[3:].isdigit()):
        print("❌ Invalid expiry date format.")
        return False
    if not (cvv.isdigit() and len(cvv) == 3):
        print("❌ Invalid CVV.")
        return False

    print("Processing payment...")
    print("✅ Payment successful!")
    return True


def buy_ticket():
    if not shows:
        print("No shows available.")
        return

    client_id = input("Enter your ID (real or system ID): ").strip()

    if client_id not in clients:
        print("Client not registered. Please log in first.")
        return

    client_name = clients[client_id]["name"]

    print("\nAvailable Shows:")
    for i, show in enumerate(shows):
        sold_tickets = show['sold_tickets']
        total_capacity = show['venue']['capacity']
        demand_percentage = (sold_tickets / total_capacity) * 100

        price = show['base_price']
        if demand_percentage >= 90:
            price *= 1.4
        elif demand_percentage >= 75:
            price *= 1.2
        elif demand_percentage >= 50:
            price *= 1.1

        print(
            f"{i + 1}. {show['artist']['name']} at {show['venue']['name']} on {show['date']} - Ticket Price: ${price:.2f}")

    try:
        show_choice = int(input("Choose a show (number): ")) - 1
        if show_choice < 0 or show_choice >= len(shows):
            print("Invalid choice.")
            return

        show = shows[show_choice]
        seats = show['seats']

        print("\nSeating Arrangement (S: Stage, [ ]: Available, [X]: Taken, [B]: Blocked)")
        for row in seats:
            print(" ".join(row))
        print("      S T A G E      ")

        try:
            row = int(input("Choose a row (starting from 1): ")) - 1
            col = int(input("Choose a seat (starting from 1): ")) - 1

            if row < 0 or row >= len(seats) or col < 0 or col >= len(seats[0]):
                print("Invalid seat selection.")
                return

            if seats[row][col] in ('[X]', '[B]'):
                print("Seat unavailable. Please choose another.")
                return

            # Adjust price based on demand
            sold_tickets = show['sold_tickets']
            total_capacity = show['venue']['capacity']
            demand_percentage = (sold_tickets / total_capacity) * 100
            final_price = show['base_price']

            if demand_percentage >= 90:
                final_price *= 1.4
            elif demand_percentage >= 75:
                final_price *= 1.2
            elif demand_percentage >= 50:
                final_price *= 1.1

            # Process payment before finalizing the purchase
            if not process_credit_card_payment(final_price):
                print("❌ Payment failed. Purchase canceled.")
                return

            # Mark seat as sold
            seats[row][col] = '[X]'
            show['sold_tickets'] += 1

            # Store purchase details
            if client_id not in purchases:
                purchases[client_id] = {"name": client_name, "spent": 0}
            purchases[client_id]["spent"] += final_price

            print(f"✅ Ticket purchased successfully for ${final_price:.2f}!")

        except ValueError:
            print("Invalid input. Please enter a number.")

    except ValueError:
        print("Invalid input. Please enter a number.")



def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Create Venue")
        print("2. Create Artist")
        print("3. Create Show")
        print("4. Delete Show")
        print("5. Manage Seat Availability")
        print("6. View Show Sales")  # <-- NEW OPTION
        print("7. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            create_venue()
        elif choice == "2":
            create_artist()
        elif choice == "3":
            create_show()
        elif choice == "4":
            delete_show()
        elif choice == "5":
            manage_seats()
        elif choice == "6":  # <-- NEW FUNCTION CALL
            view_show_sales()
        elif choice == "7":
            break
        else:
            print("Invalid choice, please try again.")


def view_show_sales():
    """Calculates and displays the total sales revenue for a selected show, including client purchases."""
    if not shows:
        print("No shows available.")
        return

    print("\nAvailable Shows:")
    for i, show in enumerate(shows):
        print(f"{i + 1}. {show['artist']['name']} at {show['venue']['name']} on {show['date']}")

    try:
        show_choice = int(input("Choose a show to view sales (number): ")) - 1
        if show_choice < 0 or show_choice >= len(shows):
            print("Invalid choice.")
            return

        show = shows[show_choice]
        base_price = show['base_price']
        sold_tickets = show['sold_tickets']
        total_capacity = show['venue']['capacity']
        demand_percentage = (sold_tickets / total_capacity) * 100

        # Adjusted ticket price based on demand
        final_price = base_price
        if demand_percentage >= 90:
            final_price *= 1.4
        elif demand_percentage >= 75:
            final_price *= 1.2
        elif demand_percentage >= 50:
            final_price *= 1.1

        total_sales = sold_tickets * final_price
        print(f"\nTotal sales revenue for {show['artist']['name']} at {show['venue']['name']} on {show['date']}: ${total_sales:.2f}")

        # Display individual client spending
        print("\nClient Purchases:")
        if not purchases:
            print("No purchases have been made yet.")
        else:
            for client_id, data in purchases.items():
                print(f"🔹 {data['name']} (ID: {client_id}) - Spent: ${data['spent']:.2f}")

    except ValueError:
        print("Invalid input. Please enter a number.")




def create_venue():
    name = input("Enter venue name: ")
    capacity = int(input("Enter venue capacity: "))

    # ✅ Automatically calculate rows & seats per row
    rows = math.isqrt(capacity)  # Get the square root of the capacity
    seats_per_row = math.ceil(capacity / rows)  # Divide total seats across rows

    venues.append({"name": name, "capacity": capacity, "rows": rows, "seats_per_row": seats_per_row})
    print(f"Venue '{name}' created successfully with {rows} rows and {seats_per_row} seats per row!")

def create_artist():
    name = input("Enter artist name: ")
    genre = input("Enter artist genre: ")
    artists.append({"name": name, "genre": genre})
    print("Artist created successfully.")


def create_show():
    if not venues or not artists:
        print("You need to create venues and artists first.")
        return

    print("Available Venues:")
    for i, venue in enumerate(venues):
        print(
            f"{i + 1}. {venue['name']} - Capacity: {venue['capacity']} ({venue['rows']} rows x {venue['seats_per_row']} seats per row)")

    try:
        venue_choice = int(input("Choose a venue (number): ")) - 1
        if not (0 <= venue_choice < len(venues)):
            print("Invalid choice. Please select a valid venue number.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    venue = venues[venue_choice]

    print("Available Artists:")
    for i, artist in enumerate(artists):
        print(f"{i + 1}. {artist['name']} ({artist['genre']})")

    try:
        artist_choice = int(input("Choose an artist (number): ")) - 1
        if not (0 <= artist_choice < len(artists)):
            print("Invalid choice. Please select a valid artist number.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    date = input("Enter show date (YYYY-MM-DD): ")

    artist = artists[artist_choice]
    base_suggestion, max_suggestion = recommend_dynamic_pricing(artist['genre'], venue['name'], artist['name'])
    if base_suggestion and max_suggestion:
        print(f"💡 Suggested price range: ${base_suggestion} - ${max_suggestion}")
    else:
        print("⚠️ No past data available for dynamic pricing.")

    try:
        base_price = float(input("Enter base ticket price: "))
        if base_price < 0:
            print("Price cannot be negative.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid price.")
        return

    # ✅ Use the venue's automatically calculated rows & seats per row
    rows = venue["rows"]
    seats_per_row = venue["seats_per_row"]
    seats = [['[ ]' for _ in range(seats_per_row)] for _ in range(rows)]

    shows.append({
        "venue": venue,
        "artist": artists[artist_choice],
        "date": date,
        "base_price": base_price,
        "sold_tickets": 0,
        "seats": seats
    })

    print("Show created successfully.")


def delete_show():
    if not shows:
        print("No shows available to delete.")
        return

    print("\nAvailable Shows:")
    for i, show in enumerate(shows):
        print(f"{i + 1}. {show['artist']['name']} at {show['venue']['name']} on {show['date']}")

    try:
        show_choice = int(input("Choose a show to delete (number): ")) - 1
        if show_choice < 0 or show_choice >= len(shows):
            print("Invalid choice.")
            return

        del shows[show_choice]
        print("Show deleted successfully.")

    except ValueError:
        print("Invalid input. Please enter a number.")


def manage_seats():
    if not shows:
        print("No shows available.")
        return

    print("\nAvailable Shows:")
    for i, show in enumerate(shows):
        print(f"{i + 1}. {show['artist']['name']} at {show['venue']['name']} on {show['date']}")

    try:
        show_choice = int(input("Choose a show to manage seats (number): ")) - 1
        if show_choice < 0 or show_choice >= len(shows):
            print("Invalid choice.")
            return

        show = shows[show_choice]
        seats = show['seats']
        rows = len(seats)
        cols = len(seats[0])

        while True:
            print("\nSeating Arrangement (S: Stage, [ ]: Available, [X]: Taken, [B]: Blocked)")
            for row in seats:
                print(" ".join(row))
            print("      S T A G E      ")

            action = input("Enter 'B' to block, 'U' to unblock, or 'Q' to quit: ").strip().upper()
            if action == 'Q':
                break

            try:
                row = int(input(f"Choose row (1 to {rows}): ")) - 1
                col = int(input(f"Choose column (1 to {cols}): ")) - 1

                if 0 <= row < rows and 0 <= col < cols:
                    if action == 'B':
                        if seats[row][col] == '[X]':
                            print("❌ Cannot block an already taken seat.")
                        else:
                            seats[row][col] = '[B]'
                            print("✅ Seat blocked successfully.")
                    elif action == 'U':
                        if seats[row][col] == '[B]':
                            seats[row][col] = '[ ]'
                            print("✅ Seat unblocked successfully.")
                        else:
                            print("❌ This seat is not blocked.")
                    else:
                        print("❌ Invalid action.")
                else:
                    print("❌ Invalid seat selection. Please enter a valid row and column.")

            except ValueError:
                print("❌ Invalid input. Please enter a number.")

    except ValueError:
        print("❌ Invalid input. Please enter a number.")


def main_menu():
    while True:
        print("\nWelcome to the Event Management System")
        print("1. Client Login")
        print("2. Admin Login")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            client_login()
        elif choice == "2":
            admin_menu()
        elif choice == "3":
            print("Exiting the system...")
            break
        else:
            print("Invalid choice, please try again.")

# (Your other functions like search_shows(), buy_ticket(), admin_menu(), etc., remain unchanged.)

if __name__ == "__main__":
    main_menu()
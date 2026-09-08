# Store Management

A console-based store management system built with Python and SQLite.

This project was created as a personal practice project to work with relational databases, CRUD operations, transactions, inventory management, and order processing.

## Features

* Customer management
* Product management
* Customer and product search
* Edit, delete, and restore customers
* Edit, delete, and restore products
* Create orders with multiple products
* Automatic stock management
* Order cancellation with stock restoration
* Order completion
* Order history
* Sales and inventory reports
* SQLite database migrations
* Database indexes
* Foreign key constraints
* Input validation
* Transaction handling with commit and rollback
* Soft delete and restore functionality

## Technologies

* Python
* SQLite
* SQL

## Database Structure

The application uses four main tables:

* `customers`
* `products`
* `orders`
* `order_items`

The relationships between orders and products are handled through the `order_items` table.

## Getting Started

Clone the repository:

```bash
git clone https://github.com/Azar-Code7/Store-Management.git
```

Go to the project directory:

```bash
cd Store-Management
```

Run the application:

```bash
python main.py
```

The SQLite database will be created automatically when the application starts.

## Main Menu

The application provides options for:

1. Customer management
2. Product management
3. Order creation
4. Order management
5. Soft delete and restore
6. Reports

## Order Management

When an order is created:

* The selected products are added to the order.
* Product stock is decreased automatically.
* The price stored in `order_items` preserves the price at the time of purchase.
* The final order total is calculated from the database.

When an active order is cancelled, the purchased quantities are returned to product stock.

Completed orders cannot be cancelled.

## Database Safety

The project uses:

* Parameterized SQL queries
* Foreign key constraints
* SQLite `CHECK` constraints
* Transactions
* Rollback on database errors
* Unique indexes
* Input validation

## Project Structure

```text
Store-Management/
│
├── main.py
├── README.md
└── .gitignore
```

`store.db` is created locally when the application runs and is ignored by Git.

## Project Status

This is a personal learning and portfolio project.

The current version focuses on practicing Python, SQLite, relational database design, and real-world business logic.

## Future Improvements

Possible future improvements include:

* Better console interface
* More detailed reports
* Authentication and user roles
* Exporting reports
* Splitting the project into multiple modules

## Author

Mohammad Eshagh Azar

GitHub: https://github.com/Azar-Code7

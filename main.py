import sqlite3


DATABASE_NAME = "store.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def connect2db():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# =========================================================
# CREATE TABLES
# =========================================================

def create_tables():
    conn = connect2db()
    cursor = conn.cursor()

    try:
        query1 = """CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(70) NOT NULL,
            phone VARCHAR(20),
            is_deleted BOOLEAN DEFAULT FALSE
        )"""

        query2 = """CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            price INTEGER NOT NULL CHECK (price > 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            category VARCHAR(50),
            is_deleted BOOLEAN DEFAULT FALSE
        )"""

        query3 = """CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            total_price INTEGER NOT NULL DEFAULT 0
                CHECK (total_price >= 0),
            status VARCHAR(20) NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'completed', 'cancelled')),
            created_at TEXT DEFAULT (datetime('now')),

            FOREIGN KEY (customer_id)
                REFERENCES customers(id)
        )"""

        query4 = """CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            price INTEGER NOT NULL CHECK (price > 0),

            FOREIGN KEY (order_id)
                REFERENCES orders(id),

            FOREIGN KEY (product_id)
                REFERENCES products(id)
        )"""

        cursor.execute(query1)
        cursor.execute(query2)
        cursor.execute(query3)
        cursor.execute(query4)

        conn.commit()

        print("Database Created Successfully!")

    except sqlite3.Error:
        conn.rollback()
        print("Database Initialization Failed!")

    finally:
        conn.close()


# =========================================================
# DATABASE MIGRATION
# =========================================================

def migrate_database():
    conn = connect2db()
    cursor = conn.cursor()

    try:
        # -------------------------------------------------
        # Check orders.status
        # -------------------------------------------------

        cursor.execute("PRAGMA table_info(orders)")
        columns = cursor.fetchall()

        column_names = [column[1] for column in columns]

        if "status" not in column_names:
            cursor.execute(
                """ALTER TABLE orders
                   ADD COLUMN status TEXT DEFAULT 'active'"""
            )

            print("Orders Table Migrated Successfully!")

        # -------------------------------------------------
        # Check old customers.phone UNIQUE
        # -------------------------------------------------

        cursor.execute("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'customers'
        """)

        result = cursor.fetchone()

        if result is not None and result[0] is not None:

            customers_sql = result[0].upper()

            if "PHONE VARCHAR(20) UNIQUE" in customers_sql:
                print("Old Customer Phone Schema Detected!")
                print("Updating Customers Table...")

                # Foreign keys must be temporarily disabled
                conn.commit()
                conn.execute("PRAGMA foreign_keys = OFF")

                cursor.execute("BEGIN")

                cursor.execute("""
                    CREATE TABLE customers_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(70) NOT NULL,
                        phone VARCHAR(20),
                        is_deleted BOOLEAN DEFAULT FALSE
                    )
                """)

                cursor.execute("""
                    INSERT INTO customers_new
                    (id, name, phone, is_deleted)
                    SELECT
                        id,
                        name,
                        phone,
                        is_deleted
                    FROM customers
                """)

                cursor.execute("DROP TABLE customers")

                cursor.execute("""
                    ALTER TABLE customers_new
                    RENAME TO customers
                """)

                conn.commit()

                conn.execute("PRAGMA foreign_keys = ON")

                print("Customers Table Migrated Successfully!")

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        conn.execute("PRAGMA foreign_keys = ON")
        print("Database Migration Failed!")

    finally:
        conn.close()


# =========================================================
# CREATE INDEXES
# =========================================================

def create_indexes():
    conn = connect2db()
    cursor = conn.cursor()

    try:

        # Prevent duplicate product in the same order
        query1 = """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_order_items_order_product
            ON order_items(order_id, product_id)
        """

        cursor.execute(query1)

        # -------------------------------------------------
        # Active customer phone must be unique
        #
        # Deleted customers are ignored.
        # NULL phones are also ignored.
        # -------------------------------------------------

        query2 = """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_customers_active_phone
            ON customers(phone)
            WHERE is_deleted = 0
            AND phone IS NOT NULL
        """

        cursor.execute(query2)

        conn.commit()

        print("Database Indexes Created Successfully!")

    except sqlite3.IntegrityError:
        conn.rollback()
        print("Database Index Creation Failed!")
        print("Duplicate Active Customer Phone Numbers Exist!")

    except sqlite3.Error:
        conn.rollback()
        print("Database Index Creation Failed!")

    finally:
        conn.close()


# =========================================================
# VALIDATION FUNCTIONS
# =========================================================

def get_customer_name():

    while True:

        name = input("Enter Customer Name: ").strip()

        if name == "":
            print("Name Cannot Be Empty!")

        elif len(name) > 70:
            print("Name Cannot Be More Than 70 Characters!")

        else:
            return name


def get_phone():

    while True:

        phone = input("Enter Phone Number: ").strip()

        if phone == "":
            print("Phone Number Cannot Be Empty!")

        elif not phone.isdigit():
            print("Phone Number Must Contain Only Numbers!")

        elif len(phone) > 20:
            print("Phone Number Cannot Be More Than 20 Digits!")

        else:
            return phone


def get_product_name():

    while True:

        name = input("Enter Product Name: ").strip()

        if name == "":
            print("Product Name Cannot Be Empty!")

        elif len(name) > 100:
            print("Product Name Cannot Be More Than 100 Characters!")

        else:
            return name


def get_category():

    while True:

        category = input("Enter Category: ").strip()

        if category == "":
            print("Category Cannot Be Empty!")

        elif len(category) > 50:
            print("Category Cannot Be More Than 50 Characters!")

        else:
            return category


def get_price():

    while True:

        try:

            price = int(input("Enter Price: "))

            if price <= 0:
                print("Price Must Be Greater Than Zero!")

            else:
                return price

        except ValueError:
            print("Please Enter A Valid Number!")


def get_stock():

    while True:

        try:

            stock = int(input("Enter Stock: "))

            if stock < 0:
                print("Stock Cannot Be Negative!")

            else:
                return stock

        except ValueError:
            print("Please Enter A Valid Number!")


def get_id():

    while True:

        try:

            value = int(input("Enter ID: "))

            if value <= 0:
                print("ID Must Be Greater Than Zero!")

            else:
                return value

        except ValueError:
            print("Please Enter A Valid ID!")


def get_quantity():

    while True:

        try:

            quantity = int(input("Enter Quantity: "))

            if quantity <= 0:
                print("Quantity Must Be Greater Than Zero!")

            else:
                return quantity

        except ValueError:
            print("Please Enter A Valid Number!")


def confirm_action(message):

    while True:

        answer = input(
            message + " (y/n): "
        ).strip().lower()

        if answer == "y":
            return True

        elif answer == "n":
            return False

        else:
            print("Please Enter y or n!")


# =========================================================
# CUSTOMER FUNCTIONS
# =========================================================

def add_customer():

    print("+*+*+*+ Add Customer +*+*+*+")

    name = get_customer_name()
    phone = get_phone()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        # Only ACTIVE customers are checked
        query = """
            SELECT id
            FROM customers
            WHERE phone = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (phone,))
        customer = cursor.fetchone()

        if customer is not None:

            print("Phone Number Already Exists!")
            return

        query = """
            INSERT INTO customers
            (name, phone)
            VALUES (?, ?)
        """

        cursor.execute(query, (name, phone))

        conn.commit()

        print("Customer Added Successfully!")

    except sqlite3.IntegrityError:

        conn.rollback()
        print("Phone Number Already Exists!")

    except sqlite3.Error:

        conn.rollback()
        print("Database Error!")

    finally:

        conn.close()


def edit_customer():

    print("------- Edit Customer -------")

    customer_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, phone
            FROM customers
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if customer is None:

            print("Customer Does Not Exist!")
            return

        print()
        print("Current Customer Details:")
        print("Name:", customer[1])
        print("Phone:", customer[2])

        print()
        print("Enter New Customer Details:")

        name = get_customer_name()
        phone = get_phone()

        # Check phone against OTHER ACTIVE customers
        query = """
            SELECT id
            FROM customers
            WHERE phone = ?
            AND id != ?
            AND is_deleted = 0
        """

        cursor.execute(
            query,
            (phone, customer_id)
        )

        existing_customer = cursor.fetchone()

        if existing_customer is not None:

            print("Phone Number Already Exists!")
            return

        query = """
            UPDATE customers
            SET name = ?,
                phone = ?
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(
            query,
            (name, phone, customer_id)
        )

        if cursor.rowcount == 0:

            conn.rollback()
            print("Customer Update Failed!")
            return

        conn.commit()

        print("Customer Updated Successfully!")

    except sqlite3.IntegrityError:

        conn.rollback()
        print("Phone Number Already Exists!")

    except sqlite3.Error:

        conn.rollback()
        print("Database Error While Updating Customer!")

    finally:

        conn.close()


def show_customers():

    print("-+-+-+- Show Customers -+-+-+-")

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, phone
            FROM customers
            WHERE is_deleted = 0
            ORDER BY id
        """

        cursor.execute(query)
        customers = cursor.fetchall()

        if not customers:

            print("No Customer Found!")
            return

        print()
        print("ID | Name | Phone")

        for customer in customers:

            print(
                customer[0], "|",
                customer[1], "|",
                customer[2]
            )

    except sqlite3.Error:

        print("Database Error While Loading Customers!")

    finally:

        conn.close()


def search_customer():

    print("------- Search Customer -------")

    search = input(
        "Enter Customer Name or Phone: "
    ).strip()

    if search == "":

        print("Search Cannot Be Empty!")
        return

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, phone
            FROM customers
            WHERE is_deleted = 0
            AND (
                name LIKE ?
                OR phone LIKE ?
            )
            ORDER BY id
        """

        search_pattern = "%" + search + "%"

        cursor.execute(
            query,
            (search_pattern, search_pattern)
        )

        customers = cursor.fetchall()

        if not customers:

            print("No Customer Found!")
            return

        print()
        print("Search Results:")

        for customer in customers:

            print(
                customer[0], "|",
                customer[1], "|",
                customer[2]
            )

    except sqlite3.Error:

        print("Database Error While Searching Customers!")

    finally:

        conn.close()


def delete_customer():

    print("------- Delete Customer -------")

    customer_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        # IMPORTANT:
        # Only active customers can be deleted.
        query = """
            SELECT id, name, phone
            FROM customers
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if customer is None:

            print(
                "Customer Does Not Exist "
                "Or Is Already Deleted!"
            )
            return

        print("Customer:", customer[1])
        print("Phone:", customer[2])

        if not confirm_action(
            "Are You Sure You Want To Delete This Customer?"
        ):

            print("Delete Cancelled!")
            return

        query = """
            UPDATE customers
            SET is_deleted = 1
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (customer_id,))

        if cursor.rowcount == 0:

            conn.rollback()
            print("Customer Delete Failed!")
            return

        conn.commit()

        print("Customer Deleted Successfully!")

    except sqlite3.Error:

        conn.rollback()
        print("Delete Customer Failed!")

    finally:

        conn.close()


def show_deleted_customers():

    print("------- Deleted Customers -------")

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, phone
            FROM customers
            WHERE is_deleted = 1
            ORDER BY id
        """

        cursor.execute(query)
        customers = cursor.fetchall()

        if not customers:

            print("No Deleted Customer Found!")
            return

        print()
        print("ID | Name | Phone")

        for customer in customers:

            print(
                customer[0], "|",
                customer[1], "|",
                customer[2]
            )

    except sqlite3.Error:

        print(
            "Database Error While "
            "Loading Deleted Customers!"
        )

    finally:

        conn.close()


def restore_customer():

    print("------- Restore Customer -------")

    customer_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, phone
            FROM customers
            WHERE id = ?
            AND is_deleted = 1
        """

        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if customer is None:

            print("Deleted Customer Does Not Exist!")
            return

        print("Customer:", customer[1])
        print("Phone:", customer[2])

        # Check whether another active customer
        # already uses this phone.
        query = """
            SELECT id
            FROM customers
            WHERE phone = ?
            AND id != ?
            AND is_deleted = 0
        """

        cursor.execute(
            query,
            (customer[2], customer_id)
        )

        existing_customer = cursor.fetchone()

        if existing_customer is not None:

            print("Cannot Restore Customer!")
            print(
                "Phone Number Is Already Used "
                "By Another Customer!"
            )
            return

        if not confirm_action(
            "Are You Sure You Want To Restore This Customer?"
        ):

            print("Restore Cancelled!")
            return

        query = """
            UPDATE customers
            SET is_deleted = 0
            WHERE id = ?
            AND is_deleted = 1
        """

        cursor.execute(query, (customer_id,))

        if cursor.rowcount == 0:

            conn.rollback()
            print("Customer Restore Failed!")
            return

        conn.commit()

        print("Customer Restored Successfully!")

    except sqlite3.IntegrityError:

        conn.rollback()
        print("Cannot Restore Customer!")
        print("Phone Number Already Exists!")

    except sqlite3.Error:

        conn.rollback()
        print("Restore Customer Failed!")

    finally:

        conn.close()


# =========================================================
# PRODUCT FUNCTIONS
# =========================================================

def add_product():

    print("+++++++ Add Product +++++++")

    name = get_product_name()
    price = get_price()
    stock = get_stock()
    category = get_category()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            INSERT INTO products
            (name, price, stock, category)
            VALUES (?, ?, ?, ?)
        """

        cursor.execute(
            query,
            (name, price, stock, category)
        )

        conn.commit()

        print("Product Added Successfully!")

    except sqlite3.IntegrityError:

        conn.rollback()
        print("Invalid Product Data!")

    except sqlite3.Error:

        conn.rollback()
        print("Database Error!")

    finally:

        conn.close()


def show_products():

    print("-+-+-+- Show Products -+-+-+-")

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, price, stock, category
            FROM products
            WHERE is_deleted = 0
            ORDER BY id
        """

        cursor.execute(query)
        products = cursor.fetchall()

        if not products:

            print("No Product Found!")
            return

        print()
        print("ID | Name | Price | Stock | Category")

        for product in products:

            print(
                product[0], "|",
                product[1], "|",
                product[2], "|",
                product[3], "|",
                product[4]
            )

    except sqlite3.Error:

        print(
            "Database Error While Loading Products!"
        )

    finally:

        conn.close()


def search_product():

    print("------- Search Product -------")

    search = input(
        "Enter Product Name or Category: "
    ).strip()

    if search == "":

        print("Search Cannot Be Empty!")
        return

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, price, stock, category
            FROM products
            WHERE is_deleted = 0
            AND (
                name LIKE ?
                OR category LIKE ?
            )
            ORDER BY id
        """

        search_pattern = "%" + search + "%"

        cursor.execute(
            query,
            (search_pattern, search_pattern)
        )

        products = cursor.fetchall()

        if not products:

            print("No Product Found!")
            return

        print()
        print("Search Results:")

        for product in products:

            print(
                product[0], "|",
                product[1], "|",
                product[2], "|",
                product[3], "|",
                product[4]
            )

    except sqlite3.Error:

        print(
            "Database Error While Searching Products!"
        )

    finally:

        conn.close()


def edit_product():

    print("------- Edit Product -------")

    product_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, price, stock, category
            FROM products
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (product_id,))
        product = cursor.fetchone()

        if product is None:

            print("Product Does Not Exist!")
            return

        print()
        print("Current Product Details:")
        print("Name:", product[1])
        print("Price:", product[2])
        print("Stock:", product[3])
        print("Category:", product[4])

        print()
        print("Enter New Product Details:")

        name = get_product_name()
        price = get_price()
        stock = get_stock()
        category = get_category()

        query = """
            UPDATE products
            SET name = ?,
                price = ?,
                stock = ?,
                category = ?
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(
            query,
            (
                name,
                price,
                stock,
                category,
                product_id
            )
        )

        if cursor.rowcount == 0:

            conn.rollback()
            print("Product Update Failed!")
            return

        conn.commit()

        print("Product Updated Successfully!")

    except sqlite3.Error:

        conn.rollback()
        print(
            "Database Error While "
            "Updating Product!"
        )

    finally:

        conn.close()


def delete_product():

    print("------- Delete Product -------")

    product_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, stock
            FROM products
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (product_id,))
        product = cursor.fetchone()

        if product is None:

            print(
                "Product Does Not Exist "
                "Or Is Already Deleted!"
            )
            return

        print("Product:", product[1])
        print("Stock:", product[2])

        if product[2] > 0:

            print("Cannot Delete Product With Stock!")
            return

        if not confirm_action(
            "Are You Sure You Want To Delete This Product?"
        ):

            print("Delete Cancelled!")
            return

        query = """
            UPDATE products
            SET is_deleted = 1
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (product_id,))

        if cursor.rowcount == 0:

            conn.rollback()
            print("Product Delete Failed!")
            return

        conn.commit()

        print("Product Deleted Successfully!")

    except sqlite3.Error:

        conn.rollback()
        print("Delete Product Failed!")

    finally:

        conn.close()


def show_deleted_products():

    print("------- Deleted Products -------")

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, price, stock, category
            FROM products
            WHERE is_deleted = 1
            ORDER BY id
        """

        cursor.execute(query)
        products = cursor.fetchall()

        if not products:

            print("No Deleted Product Found!")
            return

        print()
        print("ID | Name | Price | Stock | Category")

        for product in products:

            print(
                product[0], "|",
                product[1], "|",
                product[2], "|",
                product[3], "|",
                product[4]
            )

    except sqlite3.Error:

        print(
            "Database Error While "
            "Loading Deleted Products!"
        )

    finally:

        conn.close()


def restore_product():

    print("------- Restore Product -------")

    product_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, name, price, stock, category
            FROM products
            WHERE id = ?
            AND is_deleted = 1
        """

        cursor.execute(query, (product_id,))
        product = cursor.fetchone()

        if product is None:

            print("Deleted Product Does Not Exist!")
            return

        print("Product:", product[1])
        print("Price:", product[2])
        print("Stock:", product[3])
        print("Category:", product[4])

        if not confirm_action(
            "Are You Sure You Want To Restore This Product?"
        ):

            print("Restore Cancelled!")
            return

        query = """
            UPDATE products
            SET is_deleted = 0
            WHERE id = ?
            AND is_deleted = 1
        """

        cursor.execute(query, (product_id,))

        if cursor.rowcount == 0:

            conn.rollback()
            print("Product Restore Failed!")
            return

        conn.commit()

        print("Product Restored Successfully!")

    except sqlite3.Error:

        conn.rollback()
        print("Restore Product Failed!")

    finally:

        conn.close()


# =========================================================
# ORDER FUNCTIONS
# =========================================================

def create_order():

    print("+++++++ Create Order +++++++")

    customer_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # Check active customer
        # -------------------------------------------------

        query = """
            SELECT id, name
            FROM customers
            WHERE id = ?
            AND is_deleted = 0
        """

        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()

        if customer is None:

            print("Customer Does Not Exist!")
            return

        print("Customer:", customer[1])
        print("Customer ID:", customer[0])

        # -------------------------------------------------
        # Create temporary order
        # -------------------------------------------------

        query = """
            INSERT INTO orders
            (customer_id, total_price)
            VALUES (?, ?)
        """

        cursor.execute(
            query,
            (customer_id, 0)
        )

        order_id = cursor.lastrowid

        has_items = False

        # -------------------------------------------------
        # Add products
        # -------------------------------------------------

        while True:

            print()
            print("Enter Product ID (0 to finish):")

            try:

                product_id = int(
                    input("Product ID: ")
                )

            except ValueError:

                print(
                    "Please Enter A Valid Product ID!"
                )
                continue

            if product_id == 0:
                break

            if product_id < 0:

                print(
                    "Product ID Cannot Be Negative!"
                )
                continue

            # -------------------------------------------------
            # Check active product
            # -------------------------------------------------

            query = """
                SELECT id, name, price, stock
                FROM products
                WHERE id = ?
                AND is_deleted = 0
            """

            cursor.execute(
                query,
                (product_id,)
            )

            product = cursor.fetchone()

            if product is None:

                print("Product Does Not Exist!")
                continue

            print("Product:", product[1])
            print("Price:", product[2])
            print("Stock:", product[3])

            quantity = get_quantity()

            if product[3] < quantity:

                print("Insufficient Stock!")
                continue

            # -------------------------------------------------
            # Calculate item total only for display
            # -------------------------------------------------

            item_total = product[2] * quantity

            print("Quantity:", quantity)
            print("Item Total:", item_total)

            # -------------------------------------------------
            # Check if product already exists in this order
            # -------------------------------------------------

            query = """
                SELECT id, quantity
                FROM order_items
                WHERE order_id = ?
                AND product_id = ?
            """

            cursor.execute(
                query,
                (order_id, product_id)
            )

            existing_item = cursor.fetchone()

            if existing_item is not None:

                new_quantity = (
                    existing_item[1] + quantity
                )

                query = """
                    UPDATE order_items
                    SET quantity = ?
                    WHERE id = ?
                """

                cursor.execute(
                    query,
                    (
                        new_quantity,
                        existing_item[0]
                    )
                )

            else:

                query = """
                    INSERT INTO order_items
                    (
                        order_id,
                        product_id,
                        quantity,
                        price
                    )
                    VALUES (?, ?, ?, ?)
                """

                cursor.execute(
                    query,
                    (
                        order_id,
                        product_id,
                        quantity,
                        product[2]
                    )
                )

            # -------------------------------------------------
            # Decrease stock
            # -------------------------------------------------

            query = """
                UPDATE products
                SET stock = stock - ?
                WHERE id = ?
                AND is_deleted = 0
                AND stock >= ?
            """

            cursor.execute(
                query,
                (
                    quantity,
                    product_id,
                    quantity
                )
            )

            if cursor.rowcount == 0:

                raise sqlite3.Error(
                    "Stock Update Failed!"
                )

            has_items = True

            print("Product Added To Order!")

        # -------------------------------------------------
        # Empty order protection
        # -------------------------------------------------

        if not has_items:

            print(
                "Order Must Have At Least One Product!"
            )

            conn.rollback()
            return

        # -------------------------------------------------
        # Calculate final total from database
        # -------------------------------------------------

        query = """
            SELECT COALESCE(
                SUM(quantity * price),
                0
            )
            FROM order_items
            WHERE order_id = ?
        """

        cursor.execute(
            query,
            (order_id,)
        )

        total_price = cursor.fetchone()[0]

        # -------------------------------------------------
        # Update order total
        # -------------------------------------------------

        query = """
            UPDATE orders
            SET total_price = ?
            WHERE id = ?
        """

        cursor.execute(
            query,
            (
                total_price,
                order_id
            )
        )

        conn.commit()

        print()
        print("Order Created Successfully!")
        print("Order ID:", order_id)
        print("Total Price:", total_price)

    except sqlite3.Error:

        conn.rollback()
        print("Order Creation Failed!")

    finally:

        conn.close()


def show_orders():

    print("((((((( Show Orders )))))))")

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT
                orders.id,
                customers.name,
                orders.total_price,
                orders.status,
                orders.created_at
            FROM orders
            JOIN customers
                ON orders.customer_id = customers.id
            ORDER BY orders.id
        """

        cursor.execute(query)
        orders = cursor.fetchall()

        if not orders:

            print("No Order Found!")
            return

        for order in orders:

            order_id = order[0]
            customer_name = order[1]
            total_price = order[2]
            status = order[3]
            created_at = order[4]

            print()
            print("----------------------------------------")
            print("Order ID:", order_id)
            print("Customer:", customer_name)
            print("Status:", status)
            print("Created At:", created_at)
            print("Total Price:", total_price)
            print("Products:")

            query = """
                SELECT
                    products.name,
                    order_items.quantity,
                    order_items.price
                FROM order_items
                JOIN products
                    ON order_items.product_id = products.id
                WHERE order_items.order_id = ?
            """

            cursor.execute(
                query,
                (order_id,)
            )

            items = cursor.fetchall()

            if not items:

                print("   No Items Found!")

            for item in items:

                product_name = item[0]
                quantity = item[1]
                price = item[2]

                item_total = price * quantity

                print(
                    "   -",
                    product_name,
                    "| Quantity:", quantity,
                    "| Price:", price,
                    "| Total:", item_total
                )

            print("----------------------------------------")

    except sqlite3.Error:

        print(
            "Database Error While "
            "Loading Orders!"
        )

    finally:

        conn.close()


def cancel_order():

    print("******/ Cancel Order /******")

    order_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # Check order
        # -------------------------------------------------

        query = """
            SELECT id, status
            FROM orders
            WHERE id = ?
        """

        cursor.execute(
            query,
            (order_id,)
        )

        order = cursor.fetchone()

        if order is None:

            print("Order Does Not Exist!")
            return

        order_status = order[1]

        if order_status == "cancelled":

            print("Order Already Cancelled!")
            return

        if order_status == "completed":

            print(
                "Completed Order Cannot Be Cancelled!"
            )
            return

        if order_status != "active":

            print("Order Cannot Be Cancelled!")
            return

        # -------------------------------------------------
        # Get order items
        # -------------------------------------------------

        query = """
            SELECT product_id, quantity
            FROM order_items
            WHERE order_id = ?
        """

        cursor.execute(
            query,
            (order_id,)
        )

        items = cursor.fetchall()

        if not items:

            print("Order Items Not Found!")
            return

        # -------------------------------------------------
        # Return stock
        # -------------------------------------------------

        for item in items:

            product_id = item[0]
            quantity = item[1]

            query = """
                UPDATE products
                SET stock = stock + ?
                WHERE id = ?
            """

            cursor.execute(
                query,
                (
                    quantity,
                    product_id
                )
            )

            if cursor.rowcount == 0:

                raise sqlite3.Error(
                    "Product Not Found!"
                )

        # -------------------------------------------------
        # Cancel order
        # -------------------------------------------------

        query = """
            UPDATE orders
            SET status = 'cancelled'
            WHERE id = ?
            AND status = 'active'
        """

        cursor.execute(
            query,
            (order_id,)
        )

        if cursor.rowcount == 0:

            raise sqlite3.Error(
                "Order Status Update Failed!"
            )

        conn.commit()

        print("Order Cancelled Successfully!")
        print("Stock Returned Successfully!")

    except sqlite3.Error:

        conn.rollback()
        print("Cancel Order Failed!")

    finally:

        conn.close()


def complete_order():

    print("^^^^^^^ Complete Order ^^^^^^^")

    order_id = get_id()

    conn = connect2db()
    cursor = conn.cursor()

    try:

        query = """
            SELECT id, status
            FROM orders
            WHERE id = ?
        """

        cursor.execute(
            query,
            (order_id,)
        )

        order = cursor.fetchone()

        if order is None:

            print("Order Does Not Exist!")
            return

        if order[1] == "completed":

            print("Order Already Completed!")
            return

        if order[1] == "cancelled":

            print(
                "Cancelled Order Cannot Be Completed!"
            )
            return

        if order[1] != "active":

            print("Order Cannot Be Completed!")
            return

        query = """
            UPDATE orders
            SET status = 'completed'
            WHERE id = ?
            AND status = 'active'
        """

        cursor.execute(
            query,
            (order_id,)
        )

        if cursor.rowcount == 0:

            conn.rollback()
            print("Order Status Update Failed!")
            return

        conn.commit()

        print("Order Completed Successfully!")

    except sqlite3.Error:

        conn.rollback()
        print("Complete Order Failed!")

    finally:

        conn.close()


# =========================================================
# REPORTS
# =========================================================

def show_reports():

    print()
    print("========== Store Reports ==========")

    conn = connect2db()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # Active Customers
        # -------------------------------------------------

        query = """
            SELECT COUNT(*)
            FROM customers
            WHERE is_deleted = 0
        """

        cursor.execute(query)

        active_customers = cursor.fetchone()[0]

        # -------------------------------------------------
        # Active Products
        # -------------------------------------------------

        query = """
            SELECT COUNT(*)
            FROM products
            WHERE is_deleted = 0
        """

        cursor.execute(query)

        active_products = cursor.fetchone()[0]

        # -------------------------------------------------
        # Total Stock Value
        # -------------------------------------------------

        query = """
            SELECT COALESCE(
                SUM(price * stock),
                0
            )
            FROM products
            WHERE is_deleted = 0
        """

        cursor.execute(query)

        stock_value = cursor.fetchone()[0]

        # -------------------------------------------------
        # Active Orders
        # -------------------------------------------------

        query = """
            SELECT COUNT(*)
            FROM orders
            WHERE status = 'active'
        """

        cursor.execute(query)

        active_orders = cursor.fetchone()[0]

        # -------------------------------------------------
        # Completed Orders
        # -------------------------------------------------

        query = """
            SELECT COUNT(*)
            FROM orders
            WHERE status = 'completed'
        """

        cursor.execute(query)

        completed_orders = cursor.fetchone()[0]

        # -------------------------------------------------
        # Cancelled Orders
        # -------------------------------------------------

        query = """
            SELECT COUNT(*)
            FROM orders
            WHERE status = 'cancelled'
        """

        cursor.execute(query)

        cancelled_orders = cursor.fetchone()[0]

        # -------------------------------------------------
        # Total Completed Sales
        # -------------------------------------------------

        query = """
            SELECT COALESCE(
                SUM(total_price),
                0
            )
            FROM orders
            WHERE status = 'completed'
        """

        cursor.execute(query)

        total_sales = cursor.fetchone()[0]

        # -------------------------------------------------
        # Display Reports
        # -------------------------------------------------

        print()

        print("----- Customers -----")
        print(
            "Active Customers:",
            active_customers
        )

        print()

        print("----- Products -----")
        print(
            "Active Products:",
            active_products
        )

        print(
            "Total Stock Value:",
            stock_value
        )

        print()

        print("----- Orders -----")
        print(
            "Active Orders:",
            active_orders
        )

        print(
            "Completed Orders:",
            completed_orders
        )

        print(
            "Cancelled Orders:",
            cancelled_orders
        )

        print()

        print("----- Sales -----")
        print(
            "Total Completed Sales:",
            total_sales
        )

        print()
        print("===================================")

    except sqlite3.Error:

        print(
            "Database Error While "
            "Loading Reports!"
        )

    finally:

        conn.close()


# =========================================================
# MENU
# =========================================================

def menu():

    while True:

        print()
        print("======= Store Management =======")

        print("1) Add Customer")
        print("2) Show Customers")
        print("3) Search Customer")
        print("4) Edit Customer")

        print("5) Add Product")
        print("6) Show Products")
        print("7) Search Product")
        print("8) Edit Product")

        print("9) Create Order")
        print("10) Show Orders")

        print("11) Delete Product")
        print("12) Restore Product")
        print("13) Show Deleted Products")

        print("14) Delete Customer")
        print("15) Restore Customer")
        print("16) Show Deleted Customers")

        print("17) Cancel Order")
        print("18) Complete Order")

        print("19) Reports")
        print("20) Exit")

        try:

            choice = int(
                input("Select Your Option: ")
            )

        except ValueError:

            print("Please Enter A Valid Option!")
            continue

        if choice == 1:

            add_customer()

        elif choice == 2:

            show_customers()

        elif choice == 3:

            search_customer()

        elif choice == 4:

            edit_customer()

        elif choice == 5:

            add_product()

        elif choice == 6:

            show_products()

        elif choice == 7:

            search_product()

        elif choice == 8:

            edit_product()

        elif choice == 9:

            create_order()

        elif choice == 10:

            show_orders()

        elif choice == 11:

            delete_product()

        elif choice == 12:

            restore_product()

        elif choice == 13:

            show_deleted_products()

        elif choice == 14:

            delete_customer()

        elif choice == 15:

            restore_customer()

        elif choice == 16:

            show_deleted_customers()

        elif choice == 17:

            cancel_order()

        elif choice == 18:

            complete_order()

        elif choice == 19:

            show_reports()

        elif choice == 20:

            print("GoodBye!")
            break

        else:

            print("Option Not Found!")


# =========================================================
# PROGRAM START
# =========================================================

create_tables()
migrate_database()
create_indexes()
menu()
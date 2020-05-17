import csv
import os
import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(basedir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# have to import classes after db is declared
from models.order import Order
from models.order_lines import OrderLines
from models.product_promtions import ProductPromotions
from models.vendor_commissions import Commissions


@app.route('/', methods=['GET'])
def get_report():
    """
    Generate a report when requested
    :return Search error the report:
    """
    search_date = request.args.get('date')

    # check date is in correct format
    if search_date == "" or search_date == None:
        return "You didn't provide a date. Use valid ISO-date string with the format \'YYYY-MM-DD\'"

    if not date_format_checker(search_date):
        return "Please request using a valid ISO-date string with the format \'YYYY-MM-DD\'"

    earliest_record, latest_record = get_earliest_latest_dates()
    iso_date = datetime.datetime.strptime(search_date, '%Y-%m-%d')
    if earliest_record > iso_date or latest_record < iso_date:
        return "Sorry the date is out of range, try a date between: " + earliest_record.strftime(
            '%Y-%m-%d') + " and " + latest_record.strftime('%Y-%m-%d')

    try:
        orders = db.session.query(Order).filter(Order.date == search_date).all()
        commissions = db.session.query(Commissions).filter(Order.date == search_date).all()
        product_promotions = db.session.query(ProductPromotions).filter(Order.date == search_date).all()
    except ValueError:
        return "Please initialise the database. Delete the data.db file and make sure the appropriate csv data is in the " \
               "'data_csv' directory "

    commissions_by_vendor = {}
    for commission in commissions:
        commissions_by_vendor[commission.vendor_id] = commission.rate

    promotions_by_product = {}
    promotions_on_the_day = set()
    for product in product_promotions:
        promotions_by_product[product.product_id] = product.promotion_id
        promotions_on_the_day.add(product.promotion_id)
        # assuming that each product is under one promotion each day

    try:
        # Order details
        unique_customers = set()
        total_discount_amount = 0
        item_total = 0
        discount_rate_total = 0
        order_total = 0

        # commission
        commission_total = 0
        commission_by_promotion = {}
        for promotion in promotions_on_the_day:
            commission_by_promotion[promotion] = 0

        for order in orders:
            # orders
            unique_customers.add(order.customer_id)
            item_total += sum(line.quantity for line in order.order_lines)
            total_discount_amount += sum(line.discounted_amount for line in order.order_lines)
            discount_rate_total += sum(line.discount_rate for line in order.order_lines)
            order_total += sum(line.total_amount for line in order.order_lines)

            # commissions
            commission_total += sum(
                (commissions_by_vendor[order.vendor_id] * line.discounted_amount) for line in order.order_lines)

            for line in order.order_lines:
                product = line.product_id
                if product in promotions_by_product:
                    promotion = promotions_by_product[product]
                    commission_by_promotion[promotion] += commissions_by_vendor[
                                                              order.vendor_id] * line.discounted_amount
        order_total_avg = order_total / len(orders)
        discount_rate_avg = discount_rate_total / item_total
        order_average_commission = commission_total / len(orders)

        report = {
            "customers": len(unique_customers),
            "total_discount_amount": total_discount_amount,
            "items": item_total,
            "order_total_avg": order_total_avg,
            "discount_rate_avg": discount_rate_avg,
            "commissions": {
                "promotions": commission_by_promotion,
                "total": commission_total,
                "order_average": order_average_commission
            }
        }

        return jsonify(report)
    except ValueError:
        return "Sorry, data is missing from the database. Please reinitialise."


def date_format_checker(search_date):
    """
    Check date format is in ISO
    :param search_date:
    :return: Boolean of date in correct format
    """
    try:
        datetime.datetime.strptime(search_date, '%Y-%m-%d')
    except ValueError:
        return False

    return True


def get_earliest_latest_dates():
    """
      Get the earliest and latest dates that are present in the orders table in the database
      :param :
      :return: earliest and latest order record dates
    """
    orders = db.session.query(Order).filter().all()

    earliest_record = datetime.datetime.strptime(orders[0].date, '%Y-%m-%d')
    latest_record = datetime.datetime.strptime(orders[0].date, '%Y-%m-%d')

    for order in orders[1:]:
        new_date = datetime.datetime.strptime(order.date, '%Y-%m-%d')

        if earliest_record > new_date:
            earliest_record = new_date
        if latest_record < new_date:
            latest_record = new_date

    return earliest_record, latest_record


def csv_file_to_db(csv_file):
    """
    Convert a csv file into the database
    :param csv_file as a string:
    :return:
    """
    with open(basedir + "/data_csv/" + csv_file + ".csv", 'r') as csv_input:
        csv_reader = csv.reader(csv_input, delimiter=',')

        line_count = 0
        headers = {}
        for row in csv_reader:
            if line_count == 0:
                for col, header in enumerate(row):
                    headers[header] = col
                line_count += 1
            else:
                # id, created_at, vendor_id, customer_id
                if csv_file == "orders":
                    new_entry = Order(
                        id=row[headers["id"]],
                        date=row[headers["created_at"]].split(" ")[0],
                        vendor_id=row[headers["vendor_id"]],
                        customer_id=row[headers["customer_id"]]
                    )
                elif csv_file == "order_lines":
                    new_entry = OrderLines(
                        order_id=row[headers["order_id"]],
                        product_id=row[headers["product_id"]],
                        product_price=row[headers["product_price"]],
                        discount_rate=row[headers["discount_rate"]],
                        quantity=row[headers["quantity"]],
                        full_price_amount=row[headers["full_price_amount"]],
                        discounted_amount=row[headers["discounted_amount"]],
                        total_amount=row[headers["total_amount"]]
                    )
                elif csv_file == "product_promotions":
                    new_entry = ProductPromotions(
                        date=row[headers["date"]],
                        product_id=row[headers["product_id"]],
                        promotion_id=row[headers["promotion_id"]],
                    )
                elif csv_file == "commissions":
                    new_entry = Commissions(
                        date=row[headers["date"]],
                        vendor_id=row[headers["vendor_id"]],
                        rate=row[headers["rate"]],
                    )
                else:
                    new_entry = {}

                db.session.add(new_entry)

            line_count += 1

    db.session.commit()


def initialise_db():
    """
    Initialise the database, must have a data.db file present
    :return:
    """
    db.create_all()
    csv_file_to_db("orders")
    csv_file_to_db("order_lines")
    csv_file_to_db("product_promotions")
    csv_file_to_db("commissions")

# initialise_db()

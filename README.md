<h1>Imaginary eShop</a></h1>
<p> A web framework for generating per day reports on sales. Version 1.0. </p>
<a href="localhost:5000">View Demo</a>
<br/>
<h3>Platforms and Resources used</h3>
Python3, Flask, flask_sqlalchemy, SQL 

## Application Description
The application comes pre-initialised from sample data, however for completeness the process is as follows:

1. With an empty 'data.db' SQLLite file, config sql engine to point at the file
2. Populate the db with tables created from classes defined in the models directory i.e. commissions, orders, order_lines, product_promotions. Promotions and products are not used so are currently not written in.
3. Read each relevant csv file and create a new entry that is added to the relevant table

Upon a request e.g. 'http://127.0.0.1:5000/?date=2019-09-29', the framework:
1. Checks that a date with the correct format is provided as a parameter with the get request
2. If the format is correct, extracts orders, promotions and vendor commission rates for that day
3. Compiles a report as json and returns the result

## Use with System Interpreter

Install flask and flask_sqlalchmy using pip, assuming python3 is already present on the machine:
```
pip install Flask
pip install Flask-SQLAlchemy
```

Then run the framework with:

```    
python3 -m flask run
```    

## Use with Python Virtual Environment

```
cd eShopImaginary
pip install pipenv
pipenv install
pipenv shell
```
Then run the framework with:

```    
python -m flask run
```    

## Adding new data
To add new data: 

1. Delete the data.db file
2. Put the new data in the data_csv directory, making sure the naming of the csv files is consistent with the sample data
3. Start the application with:

```    
python -m flask run
```    

## Accessing the report 
Go to 'http://127.0.0.1:5000/' or 'http://localhost:5000/'. Provide an iso-string as a date parameter e.g.

```    
'127.0.0.1:5000/?date=2019-09-29'
```

## Assumptions

* Vendor commission is taken before tax for the purposes of all calculations. This is easily configurable but default is before tax. 
* When counting the number of customers, only unique customers are counted
* Each product is only ever under one promotion each day

## Further Work
* Write more extensive python tests, using pytest in addition to returning user based responses
* Function based configuration of the database for reinitialisation from outside the application
* Create a smaller sample dataset to run more concrete testing off
* Include a more extensive report when requested
* Add to database product descriptions and promotion if they become relevant
* Use serpy serializers for better processing
* Neater report (not as raw JSON) e.g. render html page
* More code commenting

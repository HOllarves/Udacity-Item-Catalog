# Udacity Item Catalog

A nice looking item catalog with individual item and categories.

## Getting started

To properly run this website, you'll need to have the following dependencies installed:

- Flask
- httplib2
- requests
- sqlalchemy
- aouthclient

If you need any of these dependencies, make sure to install them using `pip`

This project was developed using a vagrant machine running Ubuntu.

To start the project simply run `python app.py` to start the server.

To seed the database simply run `python category_seed.py && python item_seed.py`

To use OAuth properly, you must follow [this](https://developers.google.com/api-client-library/python/guide/aaa_oauth) instructions to create your own credentials.

Visit `http://localhost:8000` to check the website.

## Features
With this website a user can log in and out using Google OAuth service. Users can perform CRUD operations on items and categories.

This application also exposes JSON endpoints for proper communications with other applications.

The following endpoints are available:

- `/categories/json`

- `/categories/show/category_id/json`

- `/categories/category_id/item/item_id/json`


## Credit
Credit to the creator of the Header-Blue theme for writing the CSS and HTML code of the header.

## License
The MIT License (MIT)

Copyright (c) 2015 Chris Kibble

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

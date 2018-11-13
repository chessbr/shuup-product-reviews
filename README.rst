Shuup Product Reviews
=====================

Product reviews addon for Shuup Platform.

Shuup is an Open Source E-Commerce Platform based on Django and Python.

https://shuup.com/

Review Flow
-----------
1. Order products
2. Create shipment, payment and mark order completed
3. Wait customer to create review.
4. Once review is received, go to admin and approve/reject reviews.
5. Setup review plugin to product detail. One for reviews summary and one for comments. Use placeholder that is shown to all products to avoid setting plugins to all products individually.

Copyright
---------

Copyright (C) 2012-2018 by Shuup Inc. <support@shuup.com>

Shuup is International Registered Trademark & Property of Shuup Inc.,
Business Address: 1013 Centre Road, Suite 403-B,
Wilmington, Delaware 19805,
United States Of America

License
-------

Shuup Product Reviews is published under Open Software License version 3.0 (OSL-3.0).
See the LICENSE file distributed with Shuup.

Some external libraries and contributions bundled with Shuup may be
published under other compatible licenses. For these, please
refer to the licenses included within each package.

Running tests
-------------

You can run tests with `py.test <http://pytest.org/>`_.

Requirements for running tests:

* Your virtualenv needs to have Shuup installed.
* Project root must be in the Python path.  This can be done with:

  .. code:: sh

     pip install -e .

To run tests, use command:

.. code:: sh

   py.test -v shuup_product_reviews_tests

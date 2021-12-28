# Product Availability Monitor

A simple script to monitor availability of products on [Kim Đồng Publisher](https://nxbkimdong.com.vn/), [IPM Vietnam](https://ipm.vn/) and [Tiki Vietnam](https://ipm.vn/).

Not all edge cases are tested. A friend of mine asked me to create this script, and a minimum viable product is enough in this use case.

## Requirements

1. Python 3 and pip (to install dependencies) if using source code directly.
2. None if running an executable on Windows.

## How to use

1. Retrieve an URL of your favorite product. For examples:
    - Kim Đồng Publisher: <https://nxbkimdong.com.vn/products/naruto-tap-67>
    - IPM Vietnam: <https://ipm.vn/products/mien-dat-hua-20>
    - Tiki Vietnam: <https://tiki.vn/dien-thoai-iphone-12-128gb-hang-chinh-hang-p123348908.html?spid=70766433>

2. Enter product to the list in terminal

3. Enter Y to confirm the list, or continue to add new product.

4. Enter an integer, which represents interval between requests, in seconds. The minimum is 1.

5. Now, the results will be shown in the console.

*Note, as there is request/response/processing time, a timestamp as shown in console is not the same as provided interval.*

## Demo

## License

Copyright (c) 2021 Hung Huu Vu.

Licensed under the [MIT license](LICENSE).

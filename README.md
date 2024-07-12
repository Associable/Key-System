# 🗝️ Python Key Generation & Redemption System

Welcome to the Python Key Generation & Redemption System! This robust system facilitates seamless key generation and redemption, making it ideal for both standalone programs and Discord bots. It also features an admin panel for managing roles and user access.

## 🚀 Key Features

- **🔒 Efficient Database Management:** Securely store and manage keys and user data.
- **🔗 Versatile Integration:** Easily integrate with standalone applications or Discord bots.
- **🛡️ Enhanced Security:** Protect your products with HWID and IP tracking.
- **🖥️ User-Friendly Interface:** Simplify key management with customizable options.
- **🔧 Extensibility:** Add new features effortlessly to meet your unique needs.
- **⚙️ Reliability:** Ensure stable operation even under heavy usage.
- **🔨 Admin Panel Integration:** Manage user roles, whitelist users, and reset HWIDs directly through Discord.

## 📜 How to Use

1. **Download or Copy `main.py`:** Place the `main.py` file into your preferred Python environment.

2. **Run the Script:** Execute the script. It will automatically check for required packages.

3. **Automatic Package Installation:** If any required packages are missing, the script will prompt you to install them automatically.

4. **Enjoy Seamless Functionality:** Once all required packages are installed, the bot will be up and running.

5. **Give Feedback:** If you like the code, please give this repository a star ⭐ so I can continue updating it!

## 🔧 Installation

To install the required packages, run:

    pip install discord pymongo colorama

## 🛠️ Bot Commands

The Python Key Generation & Redemption System includes the following Discord commands:

- **/gen_key**: Generate a new license key for a user.
- **/whitelist**: Whitelist a user by generating a key.
- **/redeem**: Redeem a license key.
- **/check_key**: Retrieve your license key.
- **/delete_key**: Unwhitelist a user by deleting their key.
- **/give-role**: Assign a role to a user.
- **/sync**: Sync the command tree (Owner only).
- **/resethwid**: Reset a user's HWID (Buyer role required).
- **/force_resethwid**: Force reset a user's HWID without cooldown (Admin only).

## 🌐 Admin Panel

For a web-based admin panel, follow these steps:

1. **Install Flask and Flask-PyMongo:**

    ```bash
    pip install flask flask-pymongo
    ```

2. **Configure Your Database:** Update the admin panel configuration with your MongoDB connection string.

3. **Deploy the Admin Panel:** You can publish the admin panel using Flask and give it its own domain. For a detailed guide on deploying a Flask app, check out [this video](https://www.youtube.com/watch?v=1FdrJPt77GU).

4. **Features of the Admin Panel:** 
   - Add and delete keys.
   - Manage whitelists.
   - Sleek and modern UI for optimal user experience.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## 🌟 Acknowledgments

- Thanks to the Discord.py and PyMongo communities for their incredible libraries.
- Special credits to [lunar](#) for inspiration.

## 📫 Contact

For any questions or issues, please reach out to [Your Email](mailto:lunaringsgg@gmail.com).

# My Subscription App

A demo subscription web application built with **FastAPI**, **Firebase Authentication**, and **Stripe**. Users can sign in with Google, view their subscriptions, and purchase a subscription via Stripe Checkout.

## Features

* Google sign-in via Firebase Authentication.
* Stripe subscription integration.
* End-to-end subscription flow:

  * Create checkout session
  * Redirect to Stripe Checkout
  * Handle success and cancel redirects
* Display active subscriptions for authenticated users.
* Responsive UI built with Tailwind CSS.
* Loading states for sign-in, subscription creation, and fetching subscriptions.

## Tech Stack

* **Backend**: FastAPI, Python
* **Authentication**: Firebase
* **Payments**: Stripe
* **Frontend**: HTML, Tailwind CSS, JavaScript
* **Database**: Firebase Firestore (storing subscription info)

---

## Project Structure

```
project-root/
│
├─ app.py
│
├─ firebase/
│   ├─ __init__.py
│   ├─ utils.py 
│
├─ templates/
│   ├─ index.html
│   ├─ subscriptions.html
│   ├─ success.html
│   └─ cancel.html
│
├─ .env.example
├─ requirements.txt
└─ README.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/luqmanAA/python-firebase-stripe.git
cd python-firebase-stripe
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` file in the root directory with:

```env
FIREBASE_CONFIG_JSON_PATH=.firebase_config.json
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

* `FIREBASE_CONFIG_JSON_PATH`: Path to your Firebase service account JSON.
* `STRIPE_SECRET_KEY`: Your Stripe secret key.
* `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key.

---

### 5. Firebase Setup

1. Create a Firebase project at [https://console.firebase.google.com](https://console.firebase.google.com).
2. Enable **Google Authentication** under Authentication → Sign-in methods.
3. Download **Service Account JSON** and place it as `.firebase_config.json` in the project root (or path specified in `.env`).

---

### 6. Stripe Setup

1. Sign up for Stripe at [https://stripe.com](https://stripe.com).
2. Create a **Product** (e.g., "Pro Subscription").
3. Create a **Price** for that product (monthly/yearly).
4. Add your **success** and **cancel** URLs as:
5. Add the secret and publishable keys to `.env`.

---

### 7. Run the App

```bash
uvicorn app:app
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Usage

1. Click **Sign in with Google** to authenticate.
2. If logged in, you will see:

   * Your name
   * **Buy Subscription** button
   * List of active subscriptions
3. Click **Buy Subscription** to open Stripe Checkout.
4. After successful payment, you will be redirected to the success page and subscription info is saved to Firebase.
5. Active subscriptions are displayed in your dashboard.

---

## Folder Details

* `firebase/utils.py`: Initializes Firebase app using the service account.
* `app.py`: FastAPI routes including:

  * `/`: Landing page
  * `/verify-token/`: Verify Firebase ID token
  * `/create-checkout-session`: Create Stripe checkout session
  * `/success`: Handle successful Stripe subscription
  * `/me/subscription`: Fetch user subscription info
* `app/templates/`: HTML templates using Tailwind and JavaScript for UI.

---

## Notes

* This demo uses **client-side Firebase authentication** and communicates ID tokens to FastAPI backend.
* Subscriptions are **saved in Firebase Firestore**, not in Stripe metadata.
* Loading states are implemented for:

  * Sign-in
  * Subscription creation
  * Fetching subscriptions

---

## Dependencies

* fastapi
* uvicorn
* firebase-admin
* python-dotenv
* stripe

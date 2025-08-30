// ===============================
// Firebase Auth State Listener
// ===============================
auth.onAuthStateChanged(async (user) => {
    if (user) {
        document.getElementById("logged-out").classList.add("hidden");
        document.getElementById("logged-in").classList.remove("hidden");
        document.getElementById("user-email").innerText = user.displayName;

        // Fetch subscriptions
        const idToken = await user.getIdToken();
        fetchSubscriptions(idToken);
    } else {
        document.getElementById("logged-in").classList.add("hidden");
        document.getElementById("logged-out").classList.remove("hidden");
    }
});

// ===============================
// Fetch Subscriptions and Update UI
// ===============================
async function fetchSubscriptions(idToken) {
    const loadingDiv = document.getElementById("subscription-loading");
    const list = document.getElementById("subscription-list");
    const noSub = document.getElementById("no-subscriptions");

    loadingDiv.classList.remove("hidden");
    list.classList.add("hidden");
    noSub.classList.add("hidden");

    try {
        const res = await fetch(`/me/subscription`, {
            method: "GET",
            headers: { "Authorization": "Bearer " + idToken },
        });
        const data = await res.json();

        list.innerHTML = "";

        if (data.subscription) {
            const sub = data.subscription;
            const card = document.createElement("div");
            card.className = "bg-gray-50 rounded-xl p-4 shadow flex justify-between items-center";
            card.innerHTML = `
                <div>
                    <p class="font-semibold text-gray-800">${sub.plan}</p>
                    <p class="text-gray-500 text-sm">Status: ${sub.status}</p>
                    <p class="text-gray-500 text-sm">Ends: ${new Date(sub.current_period_end * 1000).toLocaleDateString()}</p>
                </div>
            `;
            list.appendChild(card);

            const subBtn = document.getElementById('subscribe-btn');
            subBtn.disabled = true;
        } else {
            list.classList.remove("hidden");
            noSub.classList.remove("hidden");
        }
    } catch (err) {
        console.error("Failed to fetch subscriptions", err);
        noSub.classList.remove("hidden");
    } finally {
        loadingDiv.classList.add("hidden");
        list.classList.remove("hidden");
    }
}

// ===============================
// Google Login
// ===============================
async function login() {
    const btn = document.getElementById("google-login-btn");
    const logo = document.getElementById("google-logo");
    const text = document.getElementById("google-btn-text");
    const loading = document.getElementById("google-loading");

    btn.disabled = true;
    logo.classList.add("hidden");
    text.textContent = "Signing in...";
    loading.classList.remove("hidden");

    try {
        const provider = new firebase.auth.GoogleAuthProvider();
        const result = await auth.signInWithPopup(provider);
        const idToken = await result.user.getIdToken();

        await fetch("/verify-token/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_token: idToken })
        });
    } catch (err) {
        alert("Login failed: " + err.message);
    } finally {
        btn.disabled = false;
        logo.classList.remove("hidden");
        text.textContent = "Sign in with Google";
        loading.classList.add("hidden");
    }
}

// ===============================
// Logout
// ===============================
async function logout() {
    await auth.signOut();
}

// ===============================
// Stripe Checkout Subscription
// ===============================
async function subscribe() {
    const btn = document.getElementById("subscribe-btn");
    const text = document.getElementById("subscribe-text");
    const loading = document.getElementById("subscribe-loading");

    btn.disabled = true;
    text.textContent = "Processing...";
    loading.classList.remove("hidden");

    const user = auth.currentUser;
    if (!user) {
        alert("Please log in first.");
        resetButton();
        return;
    }

    try {
        const res = await fetch("/create-checkout-session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_token: await user.getIdToken() })
        });
        const data = await res.json();

        if (data.url) {
            window.location.href = data.url;
        } else {
            alert("Error: " + JSON.stringify(data));
            resetButton();
        }
    } catch (err) {
        alert("Subscription failed: " + err.message);
        resetButton();
    }

    function resetButton() {
        btn.disabled = false;
        text.textContent = "Buy Subscription";
        loading.classList.add("hidden");
    }
}

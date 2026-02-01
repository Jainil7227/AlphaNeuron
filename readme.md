Team AlphaNeuron
Team members -
Jainil Kothari
Kush Agarwal
Jayesh Deore
Sagar Ahirrao
Parth Kalne 

Problem Statement - Problem:

Road logistics is still planned as isolated trips rather than as a continuous operation across a vehicle's day or an operator's fleet. Load matching, routing, and pricing are decided upfront, with little ability to adapt once a truck is already on the road. As conditions change-traffic, fuel costs, delivery delays, or new load availability- trucks often run underutilized or return empty.

User Reality:

Truck drivers face idle time, uncertain income, and empty return journeys. Fleet operators managing multiple trucks struggle to coordinate vehicles that are in different locations, at different stages of a trip, and under different constraints.

Expectation:

Design an agentic system that continuously observes, decides, and acts on logistics operations as an adaptive process. The system should:

- Reason about future outcomes while vehicles are already in motion

Balance profitability, time, capacity utilization, and operational

constraints

- Support decision-making for both individual drivers and multi- truck operators

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

*   **Python 3.11+**
*   **Node.js & npm**
*   **Git**

### 🔧 Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    *   **Windows:**
        ```powershell
        python -m venv venv
        venv\Scripts\activate
        ```
    *   **Mac/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    *   Create a `.env` file in the `backend` directory.
    *   Copy contents from `.env.example` or add the following:
        ```env
        DATABASE_URL=sqlite:///./demo.db
        JWT_SECRET_KEY=your_secret_key_here
        GROK_API_KEY=your_grok_api_key_here
        DEMO_MODE=true
        ```

5.  **Run the backend server:**
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    The API will be available at `http://localhost:8000`. API Docs at `http://localhost:8000/docs`.

### 💻 Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up environment variables:**
    *   Create a `.env` file in the `frontend` directory.
    *   Add the backend URL:
        ```env
        VITE_API_URL=http://localhost:8000
        ```

4.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:5173`.

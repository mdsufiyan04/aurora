# Aurora 🌌🚢

Aurora is an advanced AI-powered route optimization application designed for Antarctic maritime navigation. It calculates safe and efficient routes through hazardous polar environments by analyzing Sea Ice Concentration (SIC), icebergs, weather, and bathymetry using A* pathfinding and Pareto optimization.

## Architecture

Aurora is a full-stack application split into two main components:

- **Frontend (`/frontend`)**: A modern, interactive web interface built with React, Vite, and MapLibre/Deck.gl. It allows users to visualize routes on a polar stereographic map, view evidence, and explore the Pareto optimal routes (Fastest, Safest, Balanced, Most Fuel Efficient).
- **Backend (`/backend`)**: A heavy-duty Python FastAPI server that uses scientific computing libraries (`xarray`, `scipy`, `geopandas`) to process Copernicus Marine Data and calculate optimal maritime routes.

## Local Development

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Git

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

### Backend Setup
1. Navigate to the root directory and create a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Mac/Linux:
   source .venv/bin/activate
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the setup scripts to download required cached data (Copernicus credentials required):
   ```bash
   ./run_setup.ps1
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Deployment

### Deploying the Frontend (Vercel)
The frontend is optimized for deployment on Vercel.
1. Create a new project in Vercel and import this repository.
2. Under **Project Settings**, set the **Root Directory** to `frontend`.
3. Add the `VITE_API_URL` environment variable and point it to your deployed backend URL.
4. Deploy!

### Deploying the Backend (Render)
Because the backend uses heavy data science libraries (`xarray`, `scipy`, etc.), it requires a robust environment like Render. It cannot be deployed on Vercel Serverless Functions.
1. Create a new **Web Service** in Render and connect this repository.
2. Leave the **Root Directory** blank.
3. Set the **Build Command** to: `pip install -r requirements.txt`
4. Set the **Start Command** to: `uvicorn backend.api.main:app --host 0.0.0.0 --port 10000`
5. Add any necessary API keys (OpenAI, Copernicus) to the Environment Variables.
6. Deploy!

# PhilGEPS Bid Opportunities - Frontend

A clean, minimal web application for browsing and searching Philippine government procurement bid opportunities.

## Features

- **Table View** - Display bid opportunities in a sortable table format
- **Smart Search** - Search across titles, reference numbers, agencies, descriptions, and categories
- **Advanced Filtering** - Filter by status, classification, and agency
- **Column Sorting** - Click any column header to sort ascending/descending
- **Detail View** - Click "View Details" to see full bid information in a modal
- **Responsive Design** - Works on desktop and mobile devices
- **Clean UI** - Minimal, easy-to-read interface with Tailwind CSS

## Tech Stack

- **React** - UI framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Mock Data** - Sample PhilGEPS bid data for development

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:5173`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── BidTable.jsx          # Main table with sorting
│   │   ├── SearchFilter.jsx      # Search and filter controls
│   │   └── BidDetailModal.jsx    # Detail view modal
│   ├── data/
│   │   └── mockBids.js           # Mock bid data
│   ├── App.jsx                   # Main app component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── tailwind.config.js            # Tailwind configuration
└── package.json
```

## Usage

### Search
Type in the search bar to filter bids across multiple fields (title, reference number, agency, description, category).

### Filter
Use the dropdown filters to narrow results by:
- **Status**: Open, Closed, Evaluation
- **Classification**: Goods, Services, Infrastructure, Consulting Services
- **Agency**: Select from available government agencies

### Sort
Click any column header to sort the table by that column. Click again to reverse the sort order.

### View Details
Click the "View Details" button on any row to see complete bid information including contact details.

## Building for Production

```bash
npm run build
```

The production-ready files will be in the `dist` folder.

## Next Steps

To connect this frontend to a real backend:

1. Replace `mockBids` import with API calls to your backend
2. Update the data fetching logic in `App.jsx`
3. Add loading states and error handling
4. Implement pagination for large datasets
5. Add authentication if needed

## API Integration Example

When you're ready to connect to your backend API:

```javascript
// In App.jsx
import { useState, useEffect } from 'react';

function App() {
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://your-backend-api.com/api/bids')
      .then(res => res.json())
      .then(data => {
        setBids(data);
        setLoading(false);
      })
      .catch(error => console.error('Error:', error));
  }, []);

  // ... rest of your component
}
```

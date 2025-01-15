import React, { useState } from 'react';
import axios from 'axios';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
} from "@mui/material";

const Trendingfood = () => {
  const [placeid, setplaceid] = useState('');
  const [trendingFoods, setTrendingFoods] = useState([]);

  const handlesubmit = async (e) => {
    e.preventDefault();
    console.log(placeid);
    const placeIDList = placeid.split(/[\s,]+/).filter((id) => id.trim() !== '');
    if (placeIDList.length < 3) {
      alert('Please enter at least three Place IDs.');
      return;
    }
    try {
      const response = await axios.post('http://localhost:5000/trendingfood', { placeids: placeIDList });
      console.log('Response:', response.data.trendingfood);
      setTrendingFoods(response.data.trendingfood);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="min-h-screen h-max  w-full bg-zinc-900 flex flex-col items-center justify-center">

      <form onSubmit={handlesubmit} className="bg-white p-6 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-4 text-gray-700">Trending Food Place IDs</h2>
        <label htmlFor="placeids" className="block text-gray-600 font-medium mb-2">
          Enter Place IDs:
        </label>
        <textarea
          id="placeids"
          value={placeid}
          onChange={(e) => setplaceid(e.target.value)}
          placeholder="Enter Place IDs here (comma, space, or newline separated)..."
          rows="5"
          className="border border-gray-300 p-3 mb-4 rounded-lg w-full resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
        ></textarea>
        <button
          type="submit"
          className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-600 transition-colors">
          Submit
        </button>
      </form>

      {/* Table displaying trending foods */}
      {/* {trendingFoods.length > 0 && (
        <div className="mt-10 w-3/4 overflow-x-auto bg-white shadow-md rounded-lg">
          <table className="table-auto w-full text-left">
            <thead className="bg-blue-500 text-white">
              <tr>
                <th className="px-4 py-2">Food Name</th>
                <th className="px-4 py-2">ARS Score</th>
                <th className="px-4 py-2">Restaurant Name</th>
                <th className="px-4 py-2">Details</th>
              </tr>
            </thead>
            <tbody>
              {trendingFoods.map((food, index) => (
                <tr key={index} className="border-t">
                  <td className="px-4 py-2">{food.name}</td>
                  <td className="px-4 py-2">{food.total_arsscore}</td>
                  <td className="px-4 py-2">
                    <ul>
                      {food.menuitems.map((item, idx) => (
                        <li key={idx}>
                          <strong>{item.restaurant}</strong>
                        </li>
                      ))}
                    </ul>
                  </td>
                  <td className="px-4 py-2">
                    <ul>
                      {food.menuitems.map((item, idx) => (
                        <li key={idx}>
                          <strong>{item.name}</strong> - {item.price} 
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )} */}
      {trendingFoods.length > 0 && (
        <TableContainer component={Paper} style={{ marginTop: "20px" }}>
          <Typography
            variant="h6"
            component="div"
            style={{ padding: "16px", fontWeight: "bold" }}
          >
            Trending Foods
          </Typography>
          <Table>
            <TableHead>
              <TableRow style={{ backgroundColor: "#1976d2", color: "#fff" }}>
                <TableCell style={{ color: "white" }}>Food Name</TableCell>
                <TableCell style={{ color: "white" }}>ARS Score</TableCell>
                <TableCell style={{ color: "white" }}>Restaurant Name</TableCell>
                <TableCell style={{ color: "white" }}>Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {trendingFoods.map((food, index) => (
                <TableRow key={index}>
                  <TableCell>{food.name}</TableCell>
                  <TableCell>{food.total_arsscore}</TableCell>
                  <TableCell>
                    <ul style={{ margin: 0, padding: 0, listStyleType: "none" }}>
                      {food.menuitems.map((item, idx) => (
                        <li key={idx}>
                          <strong>{item.restaurant}</strong>
                        </li>
                      ))}
                    </ul>
                  </TableCell>
                  <TableCell>
                    <ul style={{ margin: 0, padding: 0, listStyleType: "none" }}>
                      {food.menuitems.map((item, idx) => (
                        <li key={idx}>
                          <strong>{item.name}</strong> - {item.price}
                        </li>
                      ))}
                    </ul>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}





    </div>
  );
};

export default Trendingfood;

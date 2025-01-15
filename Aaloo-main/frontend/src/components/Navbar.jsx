import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-[red-600] shadow-lg">
      <div className="container mx-auto flex items-center justify-between py-4 px-6">
        <h1 className="text-white text-2xl font-bold">Aaloo.ai</h1>
        <ul className="flex space-x-6">
          <li>
            <Link to="/googlerestaurants" className="text-white hover:text-gray-200 transition-colors duration-200">
              Google Restaurants
            </Link>
          </li>
          <li>
            <Link to="/googlereviews" className="text-white hover:text-gray-200 transition-colors duration-200">
              Google Reviews
            </Link>
          </li>
          <li>
            <Link to="/zomatorestaurants" className="text-white hover:text-gray-200 transition-colors duration-200">
              Zomato Restaurants
            </Link>
          </li>
          <li>
            <Link to="/zomatoreviews" className="text-white hover:text-gray-200 transition-colors duration-200">
              Zomato Reviews
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;

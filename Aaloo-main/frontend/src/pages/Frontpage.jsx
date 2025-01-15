import React from "react";
import Navbar from "../components/Navbar";

const Frontpage = () => {
  return (
    <div  className="relative w-full h-screen bg-cover bg-center" style={{ backgroundImage: 'url("/public/aaloo.png")' }}>
      <Navbar />
      <div className="bg-black bg-opacity-50 w-full h-full flex flex-col items-center justify-center">
        <h1 className="text-white text-5xl font-extrabold drop-shadow-md">
          Welcome to Aaloo.ai
        </h1>
        <p className="text-gray-200 text-lg mt-4 text-center max-w-2xl">
          Your one-stop solution for restaurant data and reviews. Explore the
          best restaurants and reviews powered by Google and Zomato.
        </p>
        <button className="mt-6 px-6 py-3 bg-red-600 text-white font-medium rounded-md shadow hover:bg-red-700 transition-all">
          Get Started
        </button>
      </div>
    </div>
  );
};

export default Frontpage;

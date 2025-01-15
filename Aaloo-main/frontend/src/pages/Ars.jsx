import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Ars = () => {
    const [tableNames, setTableNames] = useState([]);
    const [googlerestaurants, setgooglerestaurants] = useState('');
    const [zomatorestaurants, setzomatorestaurants] = useState('');
    const [googlereviews, setgooglereviews] = useState('');
    const [result, setResult] = useState(null);


    useEffect(() => {
        const fetchTableNames = async () => {
            try {
                const response = await axios.get('http://localhost:5000/ars');
                setTableNames(response.data.tables.map((table) => Object.values(table)[0])); // Extract table names
            } catch (error) {
                console.error('Error fetching table names:', error);
            }
        };

        fetchTableNames();
    }, []);

    const handleCalculate = async (e) => {
        e.preventDefault();

        try {
            const response = await axios.post('http://localhost:5000/ars', {
                googlerestaurants,
                zomatorestaurants,
                googlereviews,
            });

            setResult(response.data.results);
        } catch (error) {
            console.error('Error calculating ARS:', error);
            setResult('Failed to calculate ARS. Please try again.');
        }
    };

    return (
        <div className='w-full h-screen flex justify-center items-center bg-gradient-to-r from-purple-600 to-red-600'>
            <form
                className='bg-white p-6 rounded-lg shadow-lg w-96'
                onSubmit={handleCalculate}
            >
                <h1 className='text-2xl font-bold text-gray-800 mb-6'>
                    Calculate or Update ARS
                </h1>



                <div className='mb-4'>
                    <label className='block text-gray-700 font-medium mb-2'>
                        Google Restaurants Table Name
                    </label>
                    <select
                        value={googlerestaurants}
                        onChange={(e) => setgooglerestaurants(e.target.value)}
                        className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500'
                        required
                    >
                        <option value='' disabled>
                            Select table name
                        </option>
                        {tableNames.map((table, index) => (
                            <option key={index} value={table}>
                                {table}
                            </option>
                        ))}
                    </select>
                </div>
                <div className='mb-4'>
                    <label className='block text-gray-700 font-medium mb-2'>
                        Zomato Restaurants Table Name
                    </label>
                    <select
                        value={zomatorestaurants}
                        onChange={(e) => setzomatorestaurants(e.target.value)}
                        className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500'
                        required
                    >
                        <option value='' disabled>
                            Select table name
                        </option>
                        {tableNames.map((table, index) => (
                            <option key={index} value={table}>
                                {table}
                            </option>
                        ))}
                    </select>
                </div>
                <div className='mb-4'>
                    <label className='block text-gray-700 font-medium mb-2'>
                        Google Reviews Table Name
                    </label>
                    <select
                        value={googlereviews}
                        onChange={(e) => setgooglereviews(e.target.value)}
                        className='w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500'
                        required
                    >
                        <option value='' disabled>
                            Select table name
                        </option>
                        {tableNames.map((table, index) => (
                            <option key={index} value={table}>
                                {table}
                            </option>
                        ))}
                    </select>
                </div>





                <button
                    type='submit'
                    className='w-full bg-purple-600 text-white py-2 rounded-md hover:bg-purple-700 transition duration-200'
                >
                    Calculate ARS
                </button>

                {result && (
                    <div className='mt-4 p-3 bg-gray-100 border rounded-md text-gray-800'>
                        {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
                    </div>
                )}
            </form>
        </div>
    );
};

export default Ars;

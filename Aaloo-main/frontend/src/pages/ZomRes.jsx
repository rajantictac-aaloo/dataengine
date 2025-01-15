import React, { useState } from "react";
import axios from "axios";

function ZomRes() {
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState("");
  const [message, setMessage] = useState(null);
  const [errors, setErrors] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleTableNameChange = (e) => {
    setTableName(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file || !tableName.trim()) {
      setErrors("Please provide a file and table name.");
      setMessage(null);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("tablename", tableName);

    setErrors(null);
    setMessage("Processing...");

    try {
      const response = await axios.post("http://localhost:5000/zomatorestaurants", formData,
        { headers: { "Content-Type": "multipart/form-data" }, });

      console.log(response.data.results)
      setMessage(response.data.results.db_message);
      setErrors(response.data.results);
    }
    catch (error) {
      const errorMessage = error.response.data.error;
      const details = error.response.data.details;
      setMessage(errorMessage);
      setErrors(details);
      console.log(details)

    }
  };

  return (
    <div className="min-h-screen bg-[#681024] flex items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-2xl font-semibold text-gray-800 mb-4">Zomato Restaurants</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="file" className="block text-sm font-medium text-gray-700">
              Select File
            </label>
            <input
              type="file"
              id="file"
              onChange={handleFileChange}
              className="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              accept=".csv"
            />
          </div>
          <div>
            <label htmlFor="tableName" className="block text-sm font-medium text-gray-700">
              Table Name
            </label>
            <input
              type="text"
              id="tableName"
              value={tableName}
              onChange={handleTableNameChange}
              placeholder="Enter table name"
              className="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-indigo-600 text-white font-medium rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Upload File
          </button>
        </form>

        {/* Success Message */}
        {message || !errors && (
          <div className="mt-4 p-4 bg-white border border-green-400 text-black rounded-lg">
            {message}
          </div>
        )}


        {/* Error Details */}
        {errors && (
          <div className="w-full max-w-2xl bg-white border border-black text-black px-4 py-3 rounded-lg mt-4">
            <h2 className="text-lg font-bold">Error Details:-{errors.error}</h2>



            {/* missing column errors */}
            {errors.missing_columns && (
              <div className="border text-black bg-red-200 p-3 rounded-lg">
                <strong>Missing Columns:</strong>
                <ul> {errors.missing_columns.map((col, index) => (<li key={index}>{col}</li>))}
                </ul>
              </div>)}
            {errors.extra_columns.length > 0 && (
              <div className="bg-green-200 border text-black p-3 rounded-lg">
                <strong>Extra Columns:</strong>
                <ul>{errors.extra_columns.map((col, index) => (<li key={index}>{col}</li>))}</ul>
                {<div className="font-bold text-2xl capitalize">Extra Column Found and dropped</div>}
              </div>)}

            {/* error detail for duplicates */}
            {errors.duplicates && (
              <div className="text-black">
                <strong>Duplicates - </strong>
                {<div className="text-black"><strong>The duplicate data has been dropped and the data has been cleaned of duplicates</strong></div>}

                <ul className="space-y-2">
                  {errors.duplicates.duplicate_rows && (
                    <div className="border text-black bg-red-200 p-3">
                      <strong>Complete duplicate Rows: </strong>
                      <ul>{errors.duplicates.duplicate_rows.map((row, index) => (<li key={index}>Row {row}</li>))}</ul>
                    </div>)}

                  {errors.duplicates.duplicate_place_id && (
                    <div className=" border text-black bg-red-200 p-3">
                      <strong>Duplicate Place IDs:</strong>
                      <ul>{errors.duplicates.duplicate_place_id.map((id, index) => (<li key={index}>{id}</li>))}</ul>
                    </div>
                  )}

                  {errors.duplicates.duplicate_place_id_name_address && (
                    <div className="border text-black bg-red-200 p-3">
                      <strong>Duplicate Place IDs with Name & Address:</strong>
                      <ul>{errors.duplicates.duplicate_place_id_name_address.map((entry, index) => (<li key={index}>{entry}</li>))}
                      </ul>
                    </div>)}

                  {errors.duplicates.same_place_diff_place_id && (
                    <div className="border bg-green-200 p-3">
                      <strong>Same Place with Different Place IDs:</strong>
                      <ul> {errors.duplicates.same_place_diff_place_id.map((entry, index) => (<div key={index}>{entry}</div>))}</ul>
                    </div>)}
                </ul>
              </div>
            )}



            {errors.nullvalues && (
              <div className="=text-black">
                <strong>Null Values:</strong>
                <ul className="space-y-2">
                   {/* mandaotry null values check */}
                  {errors.nullvalues.nullplaceid && (
                    <div className="text-black">
                      <strong>Null Place IDs:</strong>
                      <ul>
                        {errors.nullvalues.nullplaceid.map((id, index) => (
                          <li key={index}>{id}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {errors.nullvalues.nullrestaurantid && (
                    <div>
                      <strong>Null RestaurantID:</strong>
                      <ul>
                        {errors.nullvalues.nullrestaurantid.map((name, index) => (
                          <li key={index}>{name}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {errors.nullvalues.nulladdress && (
                    <div>
                      <strong>Null Addresses:</strong>
                      <ul>
                        {errors.nullvalues.nulladdress.map((address, index) => (
                          <li key={index}>{address}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {errors.nullvalues.nullzomatourl && (
                    <div>
                      <strong>Null ZomatoURL:</strong>
                      <ul>
                        {errors.nullvalues.nullzomatourl.map((lat, index) => (
                          <li key={index}>{lat}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {errors.nullvalues.nulltitle && (
                    <div>
                      <strong>Null Title:</strong>
                      <ul>
                        {errors.nullvalues.nulltitle.map((long, index) => (
                          <li key={index}>{long}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                </ul>
                </div>
            )}



          </div>
        )}
      </div>
    </div>
  );
}

export default ZomRes;

import React, { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

function GRestaurant() {
  const [file, setFile] = useState(null);
  const [tableName, setTableName] = useState("");
  const [message, setMessage] = useState(null);
  const [errors, setErrors] = useState(null);

  const [fillWithDefault, setFillWithDefault] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  //  function for uploading the file 
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // function for setting the table name
  const handleTableNameChange = (e) => {
    setTableName(e.target.value);
  };

  // function for submitting the form
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
      const response = await axios.post("http://localhost:5000/googlerestaurants", formData,
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

  // function for filling the default values
  const handleFillDefault = async (response) => {
    try {
      setShowConfirmation(false); // Close the modal
      const backendResponse = await axios.post("http://localhost:5000/filldefault", { response });
      if (backendResponse.status === 200) {
        setMessage("Default values applied successfully.");
        setErrors(null); // Clear errors after successful update
      }
    } catch (error) {
      setMessage("Error applying default values.");
      console.error(error);
    }
  };
  return (
    <div className="relative min-h-screen bg-[#681024] flex items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg p-8">


        <Link to="/arsvariable">
          <div className="absolute top-2 right-1 px-4 py-2 bg-yellow-300 text-black font-semibold rounded-lg shadow-md hover:bg-yellow-400 transition-all duration-200 ease-in-out">
            ARS
          </div>
        </Link>



        <h1 className="text-2xl font-semibold text-gray-800 mb-4">Google Restaurants</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="file" className="block text-sm font-medium text-gray-700">Select File</label>
            <input
              type="file"
              id="file"
              onChange={handleFileChange}
              className="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              accept=".csv" />
          </div>

          <div>
            <label htmlFor="tableName" className="block text-sm font-medium text-gray-700">Table Name</label>
            <input
              type="text"
              id="tableName"
              value={tableName}
              onChange={handleTableNameChange}
              placeholder="Enter table name"
              className="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500" />
          </div>

          <button
            type="submit"
            className="w-full py-2 px-4 bg-indigo-600 text-white font-medium rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
            Upload File</button>
        </form>

        {/* Success Message */}
        {message && (
          <div className="mt-4 p-4 bg-white border border-green-400 text-black rounded-lg">{message}</div>)
        }


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


            {/* mandaotry null values check */}
            {errors.nullvalues && (
              <div className="=text-black">
                <strong>Null Values:</strong>
                <ul className="space-y-2">
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

                {errors.nullvalues.nullname && (
                  <div>
                    <strong>Null Names:</strong>
                    <ul>
                      {errors.nullvalues.nullname.map((name, index) => (
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

                {errors.nullvalues.nulllatitude && (
                  <div>
                    <strong>Null Latitudes:</strong>
                    <ul>
                      {errors.nullvalues.nulllatitude.map((lat, index) => (
                        <li key={index}>{lat}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {errors.nullvalues.nulllongitude && (
                  <div>
                    <strong>Null Longitudes:</strong>
                    <ul>
                      {errors.nullvalues.nulllongitude.map((long, index) => (
                        <li key={index}>{long}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {errors.nullvalues.nullcategories && (
                  <div>
                    <strong>Null Categories:</strong>
                    <ul>
                      {errors.nullvalues.nullcategories.map((cat, index) => (
                        <li key={index}>{cat}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {errors.nullvalues.nullfeaturedimage && (
                  <div>
                    <strong>Null Featured Images:</strong>
                    <ul>
                      {errors.nullvalues.nullfeaturedimage.map((img, index) => (
                        <li key={index}>{img}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {errors.nullvalues.nullgooglemapsurl && (
                  <div>
                    <strong>Null Google Maps URLs:</strong>
                    <ul>
                      {errors.nullvalues.nullgooglemapsurl.map((url, index) => (
                        <li key={index}>{url}</li>
                      ))}
                    </ul>
                  </div>
                )}
               </ul>
              </div>
            )}








            {/* button for filling with default values */}
            {/* {errors.nullplaceid ||
              errors.nulladdress ||
              errors.nullcategories ||
              errors.nullfeaturedimage ||
              errors.nullgooglemapsurl ||
              errors.nulllatitude ||
              errors.nulllongitude ? (
              <button
                onClick={() => setShowConfirmation(true)}
                className="px-2 py-1 mt-4 rounded-lg bg-blue-300">
                Fill With Default Values
              </button>
            ) : null}

            {showConfirmation && (
              <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="bg-white p-6 rounded-lg shadow-lg">
                  <h2 className="text-lg font-semibold">Fill with Default Values?</h2>
                  <p className="text-sm text-gray-600 mb-4">Do you want to fill the empty mandatory fields with default values?</p>
                  <div className="flex justify-end space-x-4">
                    <button
                      onClick={() => handleFillDefault("yes")}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                      Yes
                    </button>
                    <button
                      onClick={() => setShowConfirmation(false)}
                      className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">
                      No
                    </button>
                  </div>
                </div>
              </div>
            )} */}




          </div>
        )}
      </div>
    </div>
  );
}

export default GRestaurant;

import React, { useState } from "react";
import axios from "axios";

function ZomRevi() {
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
      const response = await axios.post(
        "http://localhost:5000/zomatoreviews",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      console.log(response.data.results)

      setMessage(response.data.results.db_message);
      setErrors(response.data.results);
    }
    catch (error) {
      const errorMessage = error.response.data.error;
      const details = error.response.data.details;
      setMessage(errorMessage);
      console.log(errorMessage)
      setErrors(details);
      console.log(details)

    }
  };

  return (
    <div className="min-h-screen bg-[#681024] flex items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-2xl font-semibold text-gray-800 mb-4">Zomato Reviews</h1>
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
          <div className="mt-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
            {message}
          </div>
        )}


        {/* Error Details */}
        {errors && (
          <div className="w-full max-w-2xl bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mt-4">
            <h2 className="text-lg font-bold">Error Details:{errors.error}</h2>



            {errors.duplicates && (
              <div>
                <strong>Duplicates:</strong>
                <ul className="space-y-2">
                  {errors.duplicates.duplicate_rows && (
                    <div>
                      <strong>Duplicate Rows:</strong>
                      <ul>
                        {errors.duplicates.duplicate_rows.map((row, index) => (
                          <li key={index}>Row {row}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {errors.duplicates.duplicate_place_id && (
                    <div>
                      <strong>Duplicate Place IDs:</strong>
                      <ul>
                        {errors.duplicates.duplicate_place_id.map((id, index) => (
                          <li key={index}>{id}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {errors.duplicates.duplicate_place_id_name_address && (
                    <div>
                      <strong>Duplicate Place IDs with Name & Address:</strong>
                      <ul>
                        {errors.duplicates.duplicate_place_id_name_address.map(
                          (entry, index) => (
                            <li key={index}>{entry}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                  {errors.duplicates.same_place_diff_place_id && (
                    <div>
                      <strong>Same Place with Different Place IDs:</strong>
                      <ul>
                        {errors.duplicates.same_place_diff_place_id.map(
                          (entry, index) => (
                            <li key={index}>{entry}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                </ul>
              </div>
            )}


            {errors.missing_columns && (
              <div>
                <strong>Missing Columns:</strong>
                <ul>
                  {errors.missing_columns.map((col, index) => (
                    <li key={index}>{col}</li>
                  ))}
                </ul>
              </div>
            )}
            {errors.extra_columns.length > 0 && (
              <div>
                <strong>Extra Columns:</strong>
                <ul>
                  {errors.extra_columns.map((col, index) => (
                    <li key={index}>{col}</li>
                  ))}
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

                  {errors.nullvalues.nullreviewurl && (
                    <div>
                      <strong>Null Names:</strong>
                      <ul>
                        {errors.nullvalues.nullreviewurl.map((name, index) => (
                          <li key={index}>{name}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {errors.nullvalues.nulluserprofileurl && (
                    <div>
                      <strong>Null Addresses:</strong>
                      <ul>
                        {errors.nullvalues.nulluserprofileurl.map((address, index) => (
                          <li key={index}>{address}</li>
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

export default ZomRevi;

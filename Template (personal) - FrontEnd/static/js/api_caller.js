async function callApi(method, url, bodyData = null, csrfToken = '', media_upload=false) {
    try {
        // Validate method and URL
        if (typeof method !== 'string' || typeof url !== 'string') {
            throw new Error("Invalid method or URL");
        }

        let headers_data = {}

        if (media_upload){
            headers_data = {
                ...(csrfToken && { 'X-CSRFToken': csrfToken }),
            };
        }
        else {
            headers_data = {
                'Content-Type': 'application/json',
                ...(csrfToken && { 'X-CSRFToken': csrfToken }),
            };
        }
            
        // Prepare request options
        const options = {
            method: method.toUpperCase(),
            headers: headers_data
        };

        // Add bodyData for non-GET requests
        if (method.toUpperCase() !== 'GET' && bodyData) {
            if (media_upload){
                options.body = bodyData;            
            }
            else {
                options.body = JSON.stringify(bodyData);
            }
        }

        // Make the fetch request
        const response = await fetch(url, options);

        // Check for HTTP errors
        // if (!response.ok) {
        //     throw new Error(`HTTP Error: ${response.status} - ${response.statusText}`);
        // }

        // Parse the JSON response
        const data = await response.json();

        // Return success flag and data
        return [true, data];
    } catch (error) {
        // Log and return failure flag with error
        console.error("API Call Error:", error);
        return [false, error.message || "An unknown error occurred"];
    }
}

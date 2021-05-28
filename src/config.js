/* File name: config.js
 * Author: Queues Team
 * Description: Creates axios instance and sets its base URL.
 */

import axios from 'axios';

// Create the axios object used to interact with the API
const api = axios.create({
    // This gets changed for production, but this works for local dev
    baseURL: 'http://localhost:1337/api/'
});

export default api;

/* File name: temp.js
 * Author: @nouryehia
 * Description: Contains a temp route that can be deleted after Frontend setup.
 */

import React, {useState, useEffect} from 'react' // React components
import server from "../server" // Server methods
import '../style/temp.css' // Stylesheet

/* Route name: Temp
 * Author: @nouryehia
 * Description: Displays the name of a user based on given id.
 */
export default function Temp() {
    const [name, setName] = useState(""); // Holds name
    const user_id = 1 // User id being queried

    // Retrieve name
    useEffect(() => {
        server.getName(user_id)
            .then((response) => {
                setName(response.data.result)
            })
            .catch((err) => console.log(err))
    }, [])

    // Display html
    return (
        <div>
            <h1>User id: {user_id}</h1>
            <h1>Name: {name}</h1>
        </div>
    )
}
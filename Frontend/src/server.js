/* File name: server.js
 * Author: Queues Team, @nouryehia
 * Description: Contains all of our HTTP requests
 */

import api from "./config"

const server = {
    /* Method name: getName
     * Author: @nouryehia
     * Description: Gets name of user with given id
     * Param: user_id:  id of user
     * Returns:
     *  { "reason": ..., "result": < name of user or null (depending on whether
     *    user exists) >}
     */
    getName(user_id) {
		const params = {user_id: user_id}
		return api.get("user/get_name", {params: params})
	}
}

export default server;

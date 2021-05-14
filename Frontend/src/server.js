/* File name: server.js
 * Author: Queues Team, @nouryehia
 * Description: Contains all of our HTTP requests.
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
		const params = {user_id: user_id};
		return api.get("user/get_name", {params: params});
	},

	/* Method name: getLayouts
	 * Author: @james-c-lars
      * Description: Gets all layouts
      * Param: None
      * Returns:
      *  { "reason": ..., "result": < list of Layouts >}
      */
     getLayouts() {
          return api.get("seating_layout/get_all");
     },

	/* Method name: getLayout
	 * Author: @james-c-lars
      * Description: Gets a specific layout
      * Param: A layout_id and location. Only one needs to be right
      * Returns:
      *  { "reason": ..., "result": < A Layout >}
      */
     getLayout(layout_id, location) {
		const params = {layout_id: layout_id, location: location};
          return api.get("seating_layout/get", {params: params});
     },

	/* Method name: addLayout
	 * Author: @james-c-lars
      * Description: Creates a Layout
      * Param: Layout
      * Returns: { "reason": ... }
      */
     addLayout(layout) {
          return api.post("seating_layout/add", layout);
     },

	/* Method name: updateLayout
	 * Author: @james-c-lars
      * Description: Updates a Layout
      * Param: Layout
      * Returns: { "reason": ... }
      */
     updateLayout(layout) {
          return api.put("seating_layout/update", layout);
     },

	/* Method name: getSeatAssignments
	 * Author: @james-c-lars
      * Description: Gets all seat assignments
      * Param: None
      * Returns:
      *  { "reason": ..., "result": < list of Seat Assignments >}
      */
     getSeatAssignments() {
          return api.get("assigned_seats/get_all");
     },

	/* Method name: addSeatAssignment
	 * Author: @james-c-lars
      * Description: Creates a Seat Assignment
      * Param: Seat Assignment
      * Returns: { "reason": ... }
      */
     addSeatAssignment(assignment) {
          return api.post("assigned_seats/add", assignment);
     },

	/* Method name: updateSeatAssignment
	 * Author: @james-c-lars
      * Description: Updates a Seat Assignment
      * Param: Seat Assignment
      * Returns: { "reason": ... }
      */
     updateSeatAssignment(assignment) {
          return api.put("assigned_seats/update", assignment);
     },

     /* Method name: getCourses
	 * Author: @james-c-lars
      * Description: Gets all courses
      * Param: None
      * Returns:
      *  { "reason": ..., "result": < list of Courses >}
      */
     getCourses() {
          return api.get("course/find_all_courses");
     },

     /* Method name: getSectionsInCourse
	 * Author: @james-c-lars
      * Description: Gets all sections in a course
      * Param: Course.id
      * Returns:
      *  { "reason": ..., "result": < list of Sections >}
      */
     getSectionsInCourse(course_id) {
          const params = {course_id: course_id};
          return api.get("section/find_all_in_course", {params: params});
     },

     /* Method name: getUsersInSection
	 * Author: @james-c-lars
      * Description: Gets all user in a Section
      * Param: Course.id, Section.id
      * Returns:
      *  { "reason": ..., "result": < list of the form {"user_info": < User >,
      *             "enrolled_user_info": < EnrolledCourse > } > }
      */
     getUsersInSection(course_id, section_id) {
          const params = {course_id: course_id, section_id: section_id};
          return api.get("enrolled_course/get_user_in_section", {params: params});
     },
}

export default server;

import Styles from "../style/SeatingStyle";
import { Grid, TextField, MenuItem, Button } from "@material-ui/core";
import { Alert } from '@material-ui/lab';
import React, { useState, useEffect } from "react";
import SeatLayout from "../components/SeatLayout";
import server from "../server";

export default function SeatAssign(props) {
    const classes = Styles.useStyles();

    // SELECTION STATES
    // An array of courses
    const [courses, setCourses] = useState([]);
    // The course id of the course chosen via the dropdown menu
    const [selectedCourse, setSelectedCourse] = useState('');
    // An array of the sections in the chosen course
    const [sections, setSections] = useState([]);
    // The section id of the section chosen via the dropdown menu
    const [selectedSection, setSelectedSection] = useState('');
    // An array of layouts inherited from the Seating page
    const layouts = props.layouts;
    // The layout id of the layout chosen via the dropdown menu
    const [selectedLayout, setSelectedLayout] = useState('');
    // An array of students in the chosen section
    const [students, setStudents] = useState([]);
    // Represents whether there are too many students for the given layout
    const [sizeError, setSizeError] = useState(false);

    // LAYOUT STATES
    // A 2D array of seats in the chosen layout
    const [seatInfo, setSeatInfo] = useState([]);
    // The number of rows of seatInfo
    const [rows, setRows] = useState(0);
    // The number of columns of seatInfo
    const [cols, setCols] = useState(0);
    // The total number of non-broken seats in the layout
    const [count, setCount] = useState(0);
    // An array containing the non-broken seats in the layout
    const [seats, setSeats] = useState([]);

    // ASSIGNMENT STATES
    // The seat assignment object being generated
    const [assignment, setAssignment] = useState({});
    // The seat selected that's being editted
    const [selectedSeat, setSelectedSeat] = useState(0);

    // SAVE STATES
    // The name given to the assignment
    const [assignmentName, setAssignmentName] = useState('');
    // Whether the assignment has been saved to the database
    const [unsaved, setUnsaved] = useState(false);
    // An array of assignments inherited from the Seating page
    const assignments = props.assignments;
    // A callback function for when we want the Seating page to update the array of assignments
    const updateAssignments = props.updateAssignments;
    // The assignment we've loaded
    const [selectedAssignment, setSelectedAssignment] = useState('');



    /*
     * Selection Menu
     */

    // Takes the layouts array and makes it into MenuItems
    function layoutsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < layouts.length; i++) {
            menuItems.push(
                <MenuItem value={layouts[i].id} key={layouts[i].id}>{layouts[i].location}</MenuItem>
            );
        }

        return menuItems;
    }

    // Takes the courses array and makes it into MenuItems
    function coursesToMenuItems() {
        let menuItems = [];

        for(let i=0; i < courses.length; i++) {
            menuItems.push(
                <MenuItem value={courses[i].id} key={courses[i].id}>{courses[i].name}</MenuItem>
            );
        }

        return menuItems;
    }

    // Takes the sections array and makes it into MenuItems
    function sectionsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < sections.length; i++) {
            menuItems.push(
                <MenuItem value={sections[i].id} key={sections[i].id}>{sections[i].section_name}</MenuItem>
            );
        }

        return menuItems;
    }

    // When the page first loads we want to get a list of courses from the database
    useEffect(() => {
        server.getCourses()
            .then((response) => {
                let newCourses = response.data.result;
                setCourses(newCourses);
            })
            .catch((err) => {
                console.error(err);
            });
    }, []);

    // When we choose a different layout, we want to update the corresponding state values
    useEffect(() => {
        let layout = findItemWithID(selectedLayout, layouts);
        if(layout === null) return;

        let newInfo = JSON.parse(layout.seats);
        setSeatInfo(newInfo);
        setRows(newInfo.length);
        setCols(newInfo[0].length);
        setCount(layout.count);

        setSeats(findSeatsInLayout(newInfo));
    }, [selectedLayout]); // eslint-disable-line react-hooks/exhaustive-deps

    // When a section is chosen we want to query the database for the students in the section
    useEffect(() => {
        server.getStudentsInSection(selectedCourse, selectedSection)
            .then((response) => {
                let newStudents = [];
                // The response from the server will have both the User data and the EnrolledCourse data
                // We just need the User data
                for(let entry of response.data.result) {
                    newStudents.push(entry.user_info)
                }

                setStudents(newStudents);
            })
            .catch((err) => {
                console.error(err);
            });
    }, [selectedSection]); // eslint-disable-line react-hooks/exhaustive-deps

    // When a course is chosen we want to update the list of sections you can select
    useEffect(() => {
        server.getSectionsInCourse(selectedCourse)
            .then((response) => {
                let newSections = response.data.result;
                setSections(newSections);
            })
            .catch((err) => {
                console.error(err);
            });
    }, [selectedCourse]);

    // A generic helper function that finds an item in a list with a given id
    function findItemWithID(id, list) {
        let item;
        for(let x of list) {
            if(x.id === id) {
                item = x;
            }
        }
        if(item === undefined) {
            return null;
        }
        return item;
    }

    // Here we scan through newInfo to create an array of seats
    // This is because newInfo will also include blank spaces and is in a 2D format
    function findSeatsInLayout(newInfo) {
        let newSeats = [];

        for(let i=0; i < newInfo.length; i++) {
            for(let j=0; j < newInfo[0].length; j++) {
                // If the seat has a label it isn't a blank space
                if(newInfo[i][j].label) {
                    newSeats.push(newInfo[i][j]);
                }
            }
        }

        // We can quickly sort the seats to be alphabetical
        return newSeats.sort((a,b) => a.label>b.label);
    }

    // Whenever our layouts prop updates we want to try and keep the correct layout selected
    useEffect(() => {
        if(selectedLayout === '') return;

        let layout = findItemWithID(selectedLayout, props.layouts);
        if(layout === null) {
            setSelectedLayout('');
        }
    }, [props.layouts]); // eslint-disable-line react-hooks/exhaustive-deps

    // If our array of students or if the number of seats in the layout changes we want
    //     to make sure that we're correctly calculating whether there's a sizeError
    useEffect(() => {
        let newSizeError = students.length > count;
        if(newSizeError !== sizeError) {
            setSizeError(newSizeError);
        }
    }, [students, count]); // eslint-disable-line react-hooks/exhaustive-deps



    /*
     * Editing
     */

    // This creates the TextField which can edit the selected seat which has been clicked on
    function selectedSeatToEditableItem() {
        // If the selected seat is out of scope don't create a TextField
        if(seats.length <= selectedSeat) return null;

        // This function will be called when the user enters a new value
        function changeValue(e) {
            let newAssignment = {...assignment};
            // If the name entered is blank we want to remove the seat assignment rather than leave it blank
            if(e.target.value === '') {
                delete newAssignment[seats[selectedSeat].label];
            } else {
                // We want to save the name as well as the PDF
                // The name will be displayed on this subpage
                // The PID will be used when we want to send out emails
                newAssignment[seats[selectedSeat].label] = {
                    name: e.target.value,
                    pid: getPIDFromName(e.target.value)
                };
            }
            // Updating the seat assignment dictionary
            setAssignment(newAssignment);
            setUnsaved(true);
        }

        return (
            <Grid item key={seats[selectedSeat].label}>
                Selected seat: {seats[selectedSeat].label}
                {/* We add some extra functionality here.
                Broken seats have a (B), left handed seats have an (L).
                If the chosen seat is broken we want to disable the ability to assign a student to it.
                If the entered name doesn't correspond to a student in the students array,
                    then alert the user with error styling */}
                <TextField
                    label={`${seats[selectedSeat].label}${seats[selectedSeat].broken ? ' (B)' : seats[selectedSeat].left ? ' (L)' : ''}`}
                    disabled={seats[selectedSeat].broken}
                    value={assignment[seats[selectedSeat].label] ? assignment[seats[selectedSeat].label].name : ''}
                    error={assignment[seats[selectedSeat].label] && assignment[seats[selectedSeat].label].pid === undefined}
                    onChange={(e) => {changeValue(e)}}
                />
            </Grid> 
        )
    }

    // This is called when the user clicks on a seat in the SeatLayout
    function chooseSeat(event, i, j) {
        let seat = seatInfo[i][j];

        if(!seat.label) return;

        // Find the index of the seat in the seats array
        let x;
        for(x=0; x < seats.length; x++) {
            if(seats[x].label === seat.label) {
                break;
            }
        }

        if(x >= seats.length) {
            console.error("Could not find seat:", seat, "in:", seats);
        }
        setSelectedSeat(x);
    }

    // Does what the name says. A helper function for the selectedSeatToEditableItem function
    function getPIDFromName(name) {
        let [lname, fname] = name.split(', ');
        let match;
        for(let student of students) {
            if(student.lname === lname && student.fname === fname) {
                match = student;
                break;
            }
        }
        if(match) return match.pid;
    }

    // Finds students in the students array who haven't been assigned a seat yet
    // It creates list of them that we can display to the user
    function unassignedStudents() {
        if(students.length === 0) return null;

        let unassignedItems = [];

        // First we create a set of student's PIDs who have been assigned
        let assignedPIDs = new Set();
        for(let seat of Object.keys(assignment)) {
            assignedPIDs.add(assignment[seat].pid);
        }

        // We copy the students array into an unassigned array
        let unassigned = [...students];

        // We iterate through the unassigned array and remove anyone whose PID
        //    is in the assignedPIDs Set
        let i=0;
        while(i < unassigned.length) {
            if(assignedPIDs.has(unassigned[i].pid)) {
                unassigned.splice(i, 1);
            } else {
                i++;
            }
        }

        // For every student left in the unassigned array we add them to the React
        for(let student of unassigned) {
            unassignedItems.push(
                <Grid item key={student.pid}>
                    {`${student.lname}, ${student.fname}`}
                </Grid>
            );
        }

        return (
            <Grid item container spacing={2} direction="column">
                <u>Unassigned Students</u>
                {unassignedItems}
            </Grid>
        )
    }

    // The meat of this page, this is the logic for how to assign an array of students to 
    //     a given layout.
    // Currently left handed seats aren't treated any differently from right handed seats
    // One way to implement treating the seats differently would be to assign left handed students
    //     to the left handed seats first, and then treat the left handed seats like aisle seats
    //     while assigning right handed students below
    // This is currently how seats are assigned:
    //     Seats are broken up into "clumps" where a clump is a set of touching seats in a row
    //     We see if we can fit all the students into the layout with 2 seats between them all
    //     While we don't have enough space to fit the students we will condense down the students in a given clump
    //          We will start with clumps that are front and center, and work our way back
    //     Once we have condensed clumps enough to fit all the students we will randomize the array of students
    //     We will iterate through the randomized list and assign students one at a time to the clumps
    //     The students will be spaced using the spacing calculated earlier for that particular clump
    function autoAssignSeats() {
        /*
         * Get the set of seat clumps
         * A seat clump is a set of adjacent seats
         */
        let seatClumps = [];
        // Iterate through the rows of the 2D seat array
        for(let i=0; i < rows; i++) {
            let clumpsInRowI = [];

            let currentClump = [];
            // Iterate through the seats in the row
            for(let j=0; j < cols; j++) {
                // If the seat is not an aisle
                if(seatInfo[i][j].label) {
                    // Add it to the current clump
                    currentClump.push(seatInfo[i][j]);
                } else if (currentClump.length > 0) {
                    // Else if the clump has ended, push it to the clumpsInRowI
                    clumpsInRowI.push({
                        clump: currentClump,
                        spacing: 3,
                    });
                    currentClump = [];
                }
                // If the seat is an aisle but isn't the end of a clump, don't do anything
            }

            // Finally push any remaining clump in the row
            if(currentClump.length > 0) {
                clumpsInRowI.push({
                    clump: currentClump,
                    spacing: 3,
                });
            }

            // Push the array of clumps in the row to the overall clump 2D array
            if(clumpsInRowI.length > 0) {
                seatClumps.push(clumpsInRowI);
            }
        }

        // ==================================================
        // The code below is used for testing and simulates a number of students
        // let students = [];
        // for(let i=0; i < 35; i++) {
        //     students.push({
        //         fname: "Student",
        //         lname: String(i),
        //         pid: `A156${13+i}`,
        //         email: `s${i}@ucsd.edu`,
        //     });
        // }
        // ==================================================

        /*
         * Mix up the list of students
         */
        let tempStudents = [...students];

        let currentIndex = tempStudents.length;
        let temporaryValue;
        let randomIndex;
        
        // While there remain elements to shuffle...
        while (0 !== currentIndex) {
        
            // Pick a remaining element...
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex -= 1;
        
            // And swap it with the current element.
            temporaryValue = tempStudents[currentIndex];
            tempStudents[currentIndex] = tempStudents[randomIndex];
            tempStudents[randomIndex] = temporaryValue;
        }

        /*
         * This function finds how many students can fit in a clump with a given spacing
         */
        function canFitInClump(clumpObj) {
            let clump = clumpObj.clump;
            let spacing = clumpObj.spacing;

            let total = 0;
            let i=0;
            while(i < clump.length) {
                if(!clump[i].broken) {
                    total++;
                    i += spacing;
                } else {
                    i += 1;
                }
            }
            return total;
        }

        /*
         * Find out how many students fit in the default spacing of 3
         */
        let totalFitting = 0;
        for(let row of seatClumps) {
            for(let clumpObj of row) {
                clumpObj.fits = canFitInClump(clumpObj);
                totalFitting += clumpObj.fits;
            }
        }

        /*
         * Figure out what clumps need to lower their spacing to fit all students
         * We compress the clumps in the middle of the row first
         * The idea being that they're easier to keep an eye on
         * Similarly we work from the front of the classroom backwards
         */
        // We don't want to compress the spacing below 1
        //  so we only repeat the code enough to bring it to 1
        for(let j=0; j < 2; j++) {
            for(let row of seatClumps) {
                // Some code to iterate from the middle of the array outwards
                let i = Math.floor(row.length / 2); // i is the clump index
                let stepdir = -1;
                for(let stepCount=0; stepCount<row.length; stepCount++, i+=stepdir*stepCount, stepdir=-stepdir) {
                    let clumpObj = row[i];

                    // Check to see if we've compressed things enough
                    if(totalFitting >= tempStudents.length) break;

                    // If not compress the current clump
                    let previouslyFit = clumpObj.fits;
                    clumpObj.spacing--;
                    clumpObj.fits = canFitInClump(clumpObj);
                    totalFitting += (clumpObj.fits - previouslyFit);
                }
                if(totalFitting >= tempStudents.length) break;
            }
            if(totalFitting >= tempStudents.length) break;
        }

        // Sanity check
        if(totalFitting < tempStudents.length) {
            console.error(`Could not fit every student in a seat. totalFitting: ${totalFitting}, students.length: ${tempStudents.length}`);
            return;
        }

        /*
         * Now that we know how spaced out the students should be in every clump
         * We can assign them to their seats
         */
        let newAssignment = {};
        for(let row of seatClumps) {
            // Some code to iterate from the middle of the array outwards
            let i = Math.floor(row.length / 2); // i is the clump index
            let stepdir = -1;
            for(let stepCount=0; stepCount<row.length; stepCount++, i+=stepdir*stepCount, stepdir=-stepdir) {
                let clumpObj = row[i];
                let clump = clumpObj.clump;

                // Check to see if we've assigned every student
                if(tempStudents.length === 0) break;

                // If not assign students to the current clump
                let j=0;
                while(j < clump.length && tempStudents.length > 0) {
                    if(!clump[j].broken) {
                        let student = tempStudents.pop();
                        newAssignment[clump[j].label] = {
                            name: `${student.lname}, ${student.fname}`,
                            pid: student.pid
                        };
                        j += clumpObj.spacing;
                    } else {
                        j += 1;
                    }
                }
            }
            if(tempStudents.length === 0) break;
        }

        setAssignment(newAssignment);
        setUnsaved(true);
    }

    



    /*
     * Saving
     */

    // Makes the array of assignments into MenuItems
    function assignmentsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < assignments.length; i++) {
            menuItems.push(
                <MenuItem value={assignments[i].id} key={assignments[i].id}>{assignments[i].assignment_name}</MenuItem>
            );
        }

        return menuItems;
    }

    // Converts the current assignment into a JSON
    function toJSON() {
        return {
            assignment_name: assignmentName,
            layout_id: selectedLayout,
            course_id: selectedCourse,
            section_id: selectedSection,
            seat_assignments: JSON.stringify(assignment),
        };
    }

    // Finds an assignment in the assignments list
    function findAssignment() {
        let assignmentData;
        for(let i=0; i < assignments.length; i++) {
            if(assignments[i].assignment_name === assignmentName) {
                assignmentData = assignments[i];
            }
        }

        return assignmentData;
    }

    // Saves the current assignment to the database
    function saveAssignment() {
        let assignmentData = findAssignment();

        // We want to update the assignment if it already exists
        // And add the assignment if not
        let func;
        if(assignmentData) {
            func = server.updateSeatAssignment;
        } else {
            func = server.addSeatAssignment;
        }

        func(toJSON())
            .then((response) => {
                updateAssignments();
            })
            .catch((err) => {
                console.error(err);
            });
        
        setUnsaved(false);
    }

    // When you load an assignment using the dropdown menu we want to update the corresponding values
    useEffect(() => {
        if(selectedAssignment === '') return;

        let assignmentData = findItemWithID(selectedAssignment, assignments);
        
        let newAssignment = JSON.parse(assignmentData.seat_assignments);
        setAssignment(newAssignment);
        setAssignmentName(assignmentData.assignment_name);

        setSelectedLayout(assignmentData.layout_id);
        setSelectedCourse(assignmentData.course_id);
        setSelectedSection(assignmentData.section_id);

        setUnsaved(false);
    }, [selectedAssignment]); // eslint-disable-line react-hooks/exhaustive-deps

    // When the assignments props gets updated we need to update the selectedAssignment
    useEffect(() => {
        let assignmentData = findAssignment();
        if(assignmentData) {
            setSelectedAssignment(assignmentData.id);
        }
    }, [props.assignments]); // eslint-disable-line react-hooks/exhaustive-deps


    // If passed a hidden prop, return null
    if(props.hidden) {
        return null;
    }
    
    return (
        <div className={classes.assignMain}>
            {/* This is the save system with saving, loading, and changing the assignmentName */}
            <Grid container id="save-system" spacing={2} wrap="nowrap">
                <Grid item xs={4}>
                    {/* Loading dropdown */}
                    <TextField select
                        label="Load"
                        value={selectedAssignment}
                        onChange={(e) => setSelectedAssignment(e.target.value)}
                    >
                        {/* The MenuItems are generated dynamically with this function */}
                        {assignmentsToMenuItems()}
                    </TextField>
                </Grid>
                <Grid item xs={4}>
                    {/* Name TextField */}
                    <TextField label="Name" value={assignmentName} onChange={(e) => setAssignmentName(e.target.value)}/>
                </Grid>
                <Grid container spacing={2} item xs wrap="nowrap">
                    {/* Save Button + the unsaved work alert */}
                    <Grid item>
                        <Button variant="contained" onClick={saveAssignment}>{findAssignment() ? "Update" : "Save"}</Button>
                    </Grid>
                    <Grid item>
                        {unsaved && <Alert severity="warning">Unsaved work</Alert>}
                    </Grid>
                </Grid>
            </Grid>
            <br />

            {/* The dropdown menus for the course, section, and layout selection + the auto assign button */}
            <Grid container spacing={2} direction="column">

                <Grid item container spacing={2}>
                    {/* Course dropdown */}
                    <Grid item xs>
                        <TextField select
                            label="Course"
                            value={selectedCourse}
                            onChange={(e) => {setSelectedCourse(e.target.value); setAssignment({}); setSelectedSection(''); setUnsaved(true);}}
                        >
                            {/* The MenuItems are generated dynamically with this function */}
                            {coursesToMenuItems()}
                        </TextField>
                    </Grid>

                    {/* Section dropdown */}
                    <Grid item xs>
                        <TextField select
                            label="Section"
                            value={selectedSection}
                            onChange={(e) => {setSelectedSection(e.target.value); setAssignment({}); setUnsaved(true);}}
                            disabled={selectedCourse === ''}
                        >
                            {/* The MenuItems are generated dynamically with this function */}
                            {sectionsToMenuItems()}
                        </TextField>
                    </Grid>
                </Grid>

                {/* Layout dropdown */}
                <Grid item>
                    <TextField select
                        label="Layout"
                        value={selectedLayout}
                        onChange={(e) => {setSelectedLayout(e.target.value); setAssignment({}); setUnsaved(true);}}
                    >
                        {/* The MenuItems are generated dynamically with this function */}
                        {layoutsToMenuItems()}
                    </TextField>
                </Grid>

                {/* Auto assign Button */}
                <Grid container spacing={2} item wrap="nowrap">
                    <Grid item>
                        <Button
                            variant="contained"
                            onClick={autoAssignSeats}
                            disabled={selectedSection === '' || !seats || sizeError}
                        >
                            Auto Assign Seats
                        </Button>
                    </Grid>
                    <Grid item>
                        {(selectedLayout !== '' && sizeError) && <Alert severity="error">Not enough seats for all students!</Alert>}
                    </Grid>
                </Grid>
            </Grid>
            <br />

            {/* The seat display */}
            <SeatLayout
                hidden={!seatInfo || selectedLayout === ''}
                rows={rows} cols={cols} assignment={assignment}
                seatInfo={seatInfo}
                handleMouseDown={chooseSeat}
            />
            <br /><br />

            {/* The TextField for manual editing + the list of unassigned students */}
            <Grid container spacing={2} wrap="nowrap">
                {selectedSeatToEditableItem()}
                {unassignedStudents()}
            </Grid>
            <br /><br />
        </div>
    );
}
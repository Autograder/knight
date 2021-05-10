import Styles from "../style/SeatingStyle";
import { Grid, TextField, MenuItem, Button } from "@material-ui/core";
import { Alert } from '@material-ui/lab';
import React, { useState, useEffect } from "react";
import SeatLayout from "../components/SeatLayout";
import server from "../server";

export default function SeatAssign(props) {
    const classes = Styles.useStyles();

    // Selection states
    const [sections, setSections] = useState([]);
    const [selectedSection, setSelectedSection] = useState('');
    const [courses, setCourses] = useState([]);
    const [selectedCourse, setSelectedCourse] = useState('');
    const [selectedLayout, setSelectedLayout] = useState('');
    const layouts = props.layouts;
    const [students, setStudents] = useState([]);
    const [sizeError, setSizeError] = useState(false);

    // Layout states
    const [seatInfo, setSeatInfo] = useState([]);
    const [rows, setRows] = useState(0);
    const [cols, setCols] = useState(0);
    const [count, setCount] = useState(0);
    const [seats, setSeats] = useState([]);

    // Assignment state
    const [assignment, setAssignment] = useState({});

    // Save states
    const [assignmentName, setAssignmentName] = useState('');
    const [unsaved, setUnsaved] = useState(false);
    const assignments = props.assignments;
    const updateAssignments = props.updateAssignments;
    const [selectedAssignment, setSelectedAssignment] = useState('');



    /*
     * Selection Menu
     */

    function layoutsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < layouts.length; i++) {
            menuItems.push(
                <MenuItem value={layouts[i].id} key={layouts[i].id}>{layouts[i].location}</MenuItem>
            );
        }

        return menuItems;
    }

    function coursesToMenuItems() {
        let menuItems = [];

        for(let i=0; i < courses.length; i++) {
            menuItems.push(
                <MenuItem value={courses[i].id} key={courses[i].id}>{courses[i].name}</MenuItem>
            );
        }

        return menuItems;
    }

    function sectionsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < sections.length; i++) {
            menuItems.push(
                <MenuItem value={sections[i].id} key={sections[i].id}>{sections[i].section_name}</MenuItem>
            );
        }

        return menuItems;
    }

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

    useEffect(() => {
        server.getUsersInSection(selectedCourse, selectedSection)
            .then((response) => {
                let newStudents = [];
                for(let entry of response.data.result) {
                    newStudents.push(entry.user_info)
                }

                setStudents(newStudents);
            })
            .catch((err) => {
                console.error(err);
            });
    }, [selectedSection]); // eslint-disable-line react-hooks/exhaustive-deps

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

    function findSeatsInLayout(newInfo) {
        let newSeats = [];

        for(let i=0; i < newInfo.length; i++) {
            for(let j=0; j < newInfo[0].length; j++) {
                if(newInfo[i][j].label) {
                    newSeats.push(newInfo[i][j]);
                }
            }
        }

        return newSeats;
    }

    useEffect(() => {
        if(selectedLayout === '') return;

        let layout = findItemWithID(selectedLayout, props.layouts);
        if(layout === null) {
            setSelectedLayout('');
        }
    }, [props.layouts]); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        let newSizeError = students.length > count;
        if(newSizeError !== sizeError) {
            setSizeError(newSizeError);
        }
    }, [students, count]); // eslint-disable-line react-hooks/exhaustive-deps



    /*
     * Editing
     */
    
    function assignmentToEditableItems() {
        let items = [];

        function changeValue(e, i) {
            let newAssignment = {...assignment};
            newAssignment[seats[i].label] = e.target.value
            setAssignment(newAssignment);
            setUnsaved(true);
        }

        for(let i=0; i < seats.length; i++) {
            items.push(
                <Grid item key={seats[i].label}>
                    <TextField
                        label={`${seats[i].label}${seats[i].broken ? ' (B)' : seats[i].left ? ' (L)' : ''}`}
                        disabled={seats[i].broken}
                        value={assignment[seats[i].label] ? assignment[seats[i].label] : ''}
                        onChange={(e) => {changeValue(e,i)}}
                    />
                </Grid> 
            );
        }

        return (
            <Grid container spacing={2} direction="row">
                {items}
            </Grid>
        );
    }
    
    function autoAssignSeats() {
        /*
         * Get the set of seat clumps
         * A seat clump is a set of adjacent seats
         */
        let seatClumps = [];
        for(let i=0; i < rows; i++) {
            let clumpsInRowI = [];

            let currentClump = [];
            for(let j=0; j < cols; j++) {
                if(seatInfo[i][j].label) {
                    currentClump.push(seatInfo[i][j]);
                } else if (currentClump.length > 0) {
                    clumpsInRowI.push({
                        clump: currentClump,
                        spacing: 3,
                    });
                    currentClump = [];
                }
            }

            if(currentClump.length > 0) {
                clumpsInRowI.push({
                    clump: currentClump,
                    spacing: 3,
                });
            }

            if(clumpsInRowI.length > 0) {
                seatClumps.push(clumpsInRowI);
            }
        }

        // ==================================================
        // Remove this once we have an actual set of students
        let students = [];
        for(let i=0; i < 35; i++) {
            students.push({
                fname: "Student",
                lname: String(i),
                pid: `A156${13+i}`,
                email: `s${i}@ucsd.edu`,
            });
        }
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
                        newAssignment[clump[j].label] = `${student.fname} ${student.lname}`;
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

    function assignmentsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < assignments.length; i++) {
            menuItems.push(
                <MenuItem value={assignments[i].id} key={assignments[i].id}>{assignments[i].assignment_name}</MenuItem>
            );
        }

        return menuItems;
    }

    function toJSON() {
        return {
            assignment_name: assignmentName,
            layout_id: selectedLayout,
            course_id: selectedCourse,
            section_id: selectedSection,
            seat_assignments: JSON.stringify(assignment),
        };
    }

    function findAssignment() {
        let assignmentData;
        for(let i=0; i < assignments.length; i++) {
            if(assignments[i].assignment_name === assignmentName) {
                assignmentData = assignments[i];
            }
        }

        return assignmentData;
    }

    function saveAssignment() {
        let assignmentData = findAssignment();

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

    useEffect(() => {
        let assignmentData = findAssignment();
        if(assignmentData) {
            setSelectedAssignment(assignmentData.id);
        }
    }, [props.assignments]); // eslint-disable-line react-hooks/exhaustive-deps


    if(props.hidden) {
        return null;
    }
    
    return (
        <div className={classes.assignMain}>
            <Grid container id="save-system" spacing={2} wrap="nowrap">
                <Grid item xs={4}>
                    <TextField select
                        label="Load"
                        value={selectedAssignment}
                        onChange={(e) => setSelectedAssignment(e.target.value)}
                    >
                        {assignmentsToMenuItems()}
                    </TextField>
                </Grid>
                <Grid item xs={4}>
                    <TextField label="Name" value={assignmentName} onChange={(e) => setAssignmentName(e.target.value)}/>
                </Grid>
                <Grid container spacing={2} item xs wrap="nowrap">
                    <Grid item>
                        <Button variant="contained" onClick={saveAssignment}>{findAssignment() ? "Update" : "Save"}</Button>
                    </Grid>
                    <Grid item>
                        {unsaved && <Alert severity="warning">Unsaved work</Alert>}
                    </Grid>
                </Grid>
            </Grid>
            <br />
            <Grid container spacing={2} direction="column">
                <Grid item container spacing={2}>
                    <Grid item xs>
                        <TextField select
                            label="Course"
                            value={selectedCourse}
                            onChange={(e) => {setSelectedCourse(e.target.value); setAssignment({}); setSelectedSection(''); setUnsaved(true);}}
                        >
                            {coursesToMenuItems()}
                        </TextField>
                    </Grid>
                    <Grid item xs>
                        <TextField select
                            label="Section"
                            value={selectedSection}
                            onChange={(e) => {setSelectedSection(e.target.value); setAssignment({}); setUnsaved(true);}}
                            disabled={selectedCourse === ''}
                        >
                            {sectionsToMenuItems()}
                        </TextField>
                    </Grid>
                </Grid>
                <Grid item>
                    <TextField select
                        label="Layout"
                        value={selectedLayout}
                        onChange={(e) => {setSelectedLayout(e.target.value); setAssignment({}); setUnsaved(true);}}
                    >
                        {layoutsToMenuItems()}
                    </TextField>
                </Grid>
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
            <SeatLayout
                hidden={!seatInfo || selectedLayout === ''}
                rows={rows} cols={cols} assignment={assignment}
                seatInfo={seatInfo}
            />
            <br />
            {assignmentToEditableItems()}
        </div>
    );
}
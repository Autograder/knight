import Styles from "../style/SeatingStyle";
import { Grid, TextField, MenuItem, Button } from "@material-ui/core";
import {  } from '@material-ui/lab';
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

    // Layout states
    const [seatInfo, setSeatInfo] = useState([]);
    const [rows, setRows] = useState(0);
    const [cols, setCols] = useState(0);
    const [seats, setSeats] = useState([]);
    const [location, setLocation] = useState('');
    const [count, setCount] = useState(0);

    // Assignment states
    const [assignment, setAssignment] = useState({});

    /*
     * Selection Menu
     */

    function layoutsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < layouts.length; i++) {
            menuItems.push(
                <MenuItem value={i} key={layouts[i].id}>{layouts[i].location}</MenuItem>
            );
        }

        return menuItems;
    }

    function coursesToMenuItems() {
        let menuItems = [];

        for(let i=0; i < courses.length; i++) {
            menuItems.push(
                <MenuItem value={i} key={courses[i].id}>{courses[i].name}</MenuItem>
            );
        }

        return menuItems;
    }

    function sectionsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < sections.length; i++) {
            menuItems.push(
                <MenuItem value={i} key={sections[i].id}>{sections[i].section_name}</MenuItem>
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

    function chooseCourse(course_index) {
        setSelectedSection('');

        server.getSectionsInCourse(courses[course_index])
            .then((response) => {
                let newSections = response.data.result;
                setSections(newSections);
            })
            .catch((err) => {
                console.error(err);
            });
        
        setSelectedCourse(course_index);
    }

    function chooseSection(section_index) {
        setSelectedSection(section_index);

        server.getUsersInSection(courses[selectedCourse], sections[section_index])
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
    }

    function chooseLayout(layout_index) {
        setSelectedLayout(layout_index);

        let newInfo = JSON.parse(layouts[layout_index].seats);
        setSeatInfo(newInfo);
        setRows(newInfo.length);
        setCols(newInfo[0].length);

        setLocation(layouts[layout_index].location);
        setCount(layouts[layout_index].count);

        setSeats(findSeatsInLayout(newInfo));
    }

    function findSeatsInLayout(newInfo) {
        let newSeats = [];

        for(let i=0; i < newInfo.length; i++) {
            for(let j=0; j < newInfo[i].length; j++) {
                if(newInfo[i][j].label) {
                    newSeats.push(newInfo[i][j].label);
                }
            }
        }

        return newSeats;
    }

    useEffect(() => {
        setSelectedLayout('');
    }, [props.layouts]);

    /*
     * Editing
     */

    useEffect(() => {
        if(seats) {
            let newAssignment = {};
            for(let seat of seats) {
                newAssignment[seat] = '';
            }
            setAssignment(newAssignment);
        } else {
            setAssignment({});
        }
    }, [seats, selectedSection]);
    
    function assignmentToEditableItems() {
        let items = [];

        function changeValue(e, i) {
            let newAssignment = {...assignment};
            newAssignment[seats[i]] = e.target.value
            setAssignment(newAssignment);
        }

        for(let i=0; i < seats.length; i++) {
            items.push(
                <Grid item key={seats[i]}>
                    <TextField
                        label={seats[i]}
                        value={assignment[seats[i]] ? assignment[seats[i]] : ''}
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
    
    function assignSeats() {

    }

    if(props.hidden) {
        return null;
    }

    return (
        <div className={classes.assignMain}>
            <Grid container spacing={2} direction="column">
                <Grid item container spacing={2}>
                    <Grid item xs>
                        <TextField select
                            label="Course"
                            value={selectedCourse}
                            onChange={(e) => chooseCourse(e.target.value)}
                        >
                            {coursesToMenuItems()}
                        </TextField>
                    </Grid>
                    <Grid item xs>
                        <TextField select
                            label="Section"
                            value={selectedSection}
                            onChange={(e) => chooseSection(e.target.value)}
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
                        onChange={(e) => chooseLayout(e.target.value)}
                    >
                        {layoutsToMenuItems()}
                    </TextField>
                </Grid>
                <Grid item>
                    <Button
                        variant="contained"
                        onClick={assignSeats}
                        disabled={selectedSection === '' || selectedLayout === ''}
                    >
                        Auto Assign Seats
                    </Button>
                </Grid>
            </Grid>
            <br />
            <SeatLayout
                hidden={!seatInfo}
                rows={rows} cols={cols} assignment={assignment}
                seatInfo={seatInfo}
                handleMouseDown={() => {}}
                handleMouseUp={() => {}}
                handleMouseOver={() => {}}
                selected={new Set()}
            />
            <br />
            {assignmentToEditableItems()}
        </div>
    );
}
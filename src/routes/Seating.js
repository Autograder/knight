import OurTheme from "../style/Theme";
import Styles from "../style/SeatingStyle";
import { ThemeProvider } from "@material-ui/styles";
import { Tabs, Tab } from "@material-ui/core";
import React, { useState, useEffect } from "react";
import LayoutEditor from "../components/LayoutEditor";
import SeatAssign from "../components/SeatAssign";
import SeatEmailPDF from "../components/SeatEmailPDF";
import server from "../server"

export default function Seating() {
    const classes = Styles.useStyles();
    const theme = OurTheme.theme;

    // Selected tab represents which of the sub pages is being accessed
    const [selectedTab, setSelectedTab] = useState(0);
    // layouts is an array of Layouts
    const [layouts, setLayouts] = useState([]);
    // assignments is an array of Assignments
    const [assignments, setAssignments] = useState([]);

    // This function is called to alert the main page to do a
    // fresh GET request from the backend because something has pushed to the backend
    function updateLayouts() {
        server.getLayouts()
            .then((response) => {
                let newLayouts = response.data.result;
                setLayouts(newLayouts);
            })
            .catch((err) => {
                console.error(err);
            });
    }

    // This function is called to alert the main page to do a
    // fresh GET request from the backend because something has pushed to the backend
    function updateAssignments() {
        server.getSeatAssignments()
            .then((response) => {
                let newAssignments = response.data.result;
                setAssignments(newAssignments);
            })
            .catch((err) => {
                console.error(err);
            });
    }

    // When the page initially loads we want to make a backend request
    useEffect(() => {
        updateLayouts();
        updateAssignments();
    }, []);

    return (
        <div className={classes.root}>
            <ThemeProvider theme={theme}>
                {/* This is the selection tabs at the top of the page */}
                <Tabs value={selectedTab} onChange={(e, v) => setSelectedTab(v)}>
                    <Tab label="Layout Editor" value={0} />
                    <Tab label="Assign Seats" value={1} />
                    <Tab label="Emails/PDF" value={2} />
                </Tabs>

                {/* These are the different subpages. All but the selected one are hidden */}
                <LayoutEditor hidden={selectedTab !== 0} layouts={layouts} updateLayouts={updateLayouts} />
                <SeatAssign hidden={selectedTab !== 1} layouts={layouts} assignments={assignments} updateAssignments={updateAssignments}/>
                <SeatEmailPDF hidden={selectedTab !== 2} layouts={layouts} assignments={assignments}/>
            </ThemeProvider>
        </div>
    );
}
import Styles from "../style/SeatingStyle";
import { Grid, TextField, MenuItem, Button, InputLabel } from "@material-ui/core";
import { ToggleButton, ToggleButtonGroup, Alert } from '@material-ui/lab';
import React, { useState, useEffect } from "react";
import SeatLayout from "./SeatLayout";
import server from "../server"

// This is the grid that shows up when the page first loads
// One feature to add is the ability to create a "New Layout"
// Could reuse this as the blank board
let initSeatInfo = [];
for(let i=0; i < 15; i++) {
    initSeatInfo.push([]);
    for(let j=0; j < 15; j++) {
        initSeatInfo[i].push({label:""});
    }
}

// These aren't saved as states because they aren't really directly
//     affecting any rendering
let mouseDownCoords = null;
let invertSelection = false;

export default function LayoutEditor(props) {
    const classes = Styles.useStyles();

    // SEAT LAYOUT STATES
    // This is the 2D array of seats that are being edited
    // trueSetSeatInfo should only be called by the setSeatInfo function
    const [seatInfo, trueSetSeatInfo] = useState(initSeatInfo);
    // The number of rows of seats
    const [rows, setRows] = useState(15);
    // The number of columns of seats
    const [cols, setCols] = useState(15);

    // EDITOR STATES
    // A Set of seats which have been selected by the user
    const [selected, setSelected] = useState(new Set());
    // A Set of seats which are in the current selection of the user
    // The difference from selected is that selection is seats that are in the current selection box
    // selected is seats that were previously selected
    const [selection, setSelection] = useState(new Set());
    // This is the either left or right handed depending on which seats are selected
    // This state controls the seat type dropdown
    const [seatType, setSeatType] = useState('');
    // Either broken or not broken and controls the seat state dropdown
    const [broken, setBroken] = useState('');
    // The contents of the label TextField that appears when a single seat is selected
    const [label, setLabel] = useState('');
    // The contents of the row label TextField that appears when a single row is selected
    const [rowLabel, setRowLabel] = useState('');
    // The toggle buttons that control the direction of auto labelling
    const [mirrors, setMirrors] = useState([]);

    // SAVE STATES
    // Whether there are any duplicate seat labels in the layout
    const [hasError, setHasError] = useState(false);
    // Which layout has been selected in the load dropdown
    const [selectedLayout, setSelectedLayout] = useState('');
    // The name of the layout that is used to save the layout
    const [location, setLocation] = useState('');
    // The number of seats in the layout
    const [seatCount, setSeatCount] = useState(0);
    // Whether the layout has been saved or not
    const [unsaved, setUnsaved] = useState(false);
    // An array of layouts from the database inherited from the Seating page
    const layouts = props.layouts;
    // A callback function to have the Seating page update the array of layouts
    const updateLayouts = props.updateLayouts;

    // We don't want anyone setting the seatInfo directly
    // Rather we want to have them call this function which will perform some extra work
    // It will count the number of seats and check to see if there are any duplicate seats
    function setSeatInfo(oldInfo) {
        // Duplicate the seat array passed
        let newInfo = [...oldInfo];
        // A dictionary mapping seat labels to their position in the newInfo array
        let seatLabels = {};
        // Whether a duplicate has been found
        let newHasError = false;
        // The total number of seats counted
        let newCount = 0;

        // Iterate through the rows
        for(let i=0; i < newInfo.length; i++) {
            // Iterate through the seats in the row
            for(let j=0; j < newInfo[0].length; j++) {
                let seatLabel = newInfo[i][j].label;
                // Make sure no error carries over from last time
                delete newInfo[i][j].error;

                // If this is a blank space just skip it
                if(seatLabel === '') {
                    continue;
                // If seats with this label have been found already
                } else if(seatLabels[seatLabel] !== undefined) {
                    seatLabels[seatLabel].push([i, j]);

                    // Go through them all and mark them as having an error
                    for(let k=0; k < seatLabels[seatLabel].length; k++) {
                        let [x, y] = seatLabels[seatLabel][k];
                        newInfo[x][y].error = true;
                    }
                    // Make sure we mark that there is an overall error found as well
                    newHasError = true;
                // If no seats with this label have already been found
                } else {
                    // Add the seat and it's coords to the dict
                    seatLabels[seatLabel] = [[i, j]];
                }

                // Finally if the seat isn't broken increment our count of the seats
                if(!newInfo[i][j].broken) newCount++;
            }
        }

        trueSetSeatInfo(newInfo);
        setSeatCount(newCount);
        setHasError(newHasError);
    }

    // This function refreshes the parameters which control the editor
    function clearEditorStates() {
        setSelected(new Set());
        setSelection(new Set());
        setSeatType('');
        setBroken('');
        setLabel('');
        setRowLabel('');
        setMirrors([]);
    }



    /*
    Mouse Controls
    */

    // This function is used as a callback by the SeatLayout
    // When the mouse is pressed we want to begin a selction
    function handleMouseDown(event, i, j) {
        mouseDownCoords = [i,j];
        let newSelection = new Set();
        newSelection.add(`${i} ${j}`);

        // If the control key is held, we want this to be an inverse selection
        if(event.ctrlKey) {
            invertSelection = true;
        // Else if the shift key isn't held, we want to clear any currently selected seats
        } else if(!event.shiftKey) {
            let newSelected = new Set();
            setSelected(newSelected);
        }

        setSelection(newSelection);
    }

    // This function is used as a callback by the SeatLayout
    // When the mouse is released, we want to finalize our selection
    function handleMouseUp(event, i, j) {
        if(mouseDownCoords == null) {
            return;
        }

        // We will combine the sets of seats which have been selected with ones in the current selection
        let newSelected = combine(selected, selection);
        let newSelection = new Set();
        
        // Then we'll update the corresponding states
        setSelected(newSelected);
        setSelection(newSelection);
        mouseDownCoords = null;
        invertSelection = false;
    }


    // This function is used as a callback by the SeatLayout
    // When the mouse hovers over a box we want to change our selection
    function handleMouseOver(i, j) {
        if(mouseDownCoords == null) {
            return;
        }

        let newSelection = new Set();

        // We're finding the box between where we originally pressed down the mouse
        //     and where we've dragged it
        let iMin = Math.min(mouseDownCoords[0], i);
        let jMin = Math.min(mouseDownCoords[1], j);
        let iMax = Math.max(mouseDownCoords[0], i);
        let jMax = Math.max(mouseDownCoords[1], j);

        // We're adding all the seats in that box to the current selection set
        for(let k=iMin; k <= iMax; k++) {
            for(let l=jMin; l <= jMax; l++) {
                newSelection.add(`${k} ${l}`);
            }
        }

        setSelection(newSelection);
    }

    // This can be used to combine the selected seats with a new selection
    function combine(newSelected, newSelection) {
        let toReturn = new Set();

        // All the selected seats should be added
        for(let item of newSelected) {
            toReturn.add(item);
        }

        // If the selection is inverted, things get tricky
        if(invertSelection) {
            for(let item of newSelection) {
                if(newSelected.has(item)) {
                    toReturn.delete(item);
                } else {
                    toReturn.add(item);
                }
            }
        // If the selection isn't inverted we just want to add all seats in the selection
        } else {
            for(let item of newSelection) {
                toReturn.add(item);
            }
        }

        return toReturn;
    }

    // A helper function which transforms coordinate strings into a reference to a seat
    function decodeSelect(selectItem, arr) {
        let [i, j] = selectItem.split(' ');
        arr = arr || seatInfo;
        return arr[i][j];
    }

    // This updates the dropdown menus for seatType seatState and Label
    // We want to update them to reflect the current selection
    useEffect(() => {
        let newType = undefined;
        let newBroken = undefined;
        let newLabel = undefined;
        for(let seatCoords of combine(selected, selection)) {
            let seat = decodeSelect(seatCoords);

            if(newLabel === undefined) {
                newLabel = seat.label;
            }

            if(newType === undefined) {
                newType = seat.left;
            } else if (seat.left !== newType) {
                newType = '';
            }

            if(newBroken === undefined) {
                newBroken = seat.broken;
            } else if (seat.broken !== newBroken) {
                newBroken = '';
            }
        }

        newType = newType === undefined ? '' : newType;
        newBroken = newBroken === undefined ? '' : newBroken;
        newLabel = newLabel === undefined ? '' : newLabel;

        setSeatType(newType);
        setBroken(newBroken);
        setLabel(newLabel);
    }, [selected, selection]); // eslint-disable-line react-hooks/exhaustive-deps



    /*
    Editor Functions
    */

    // Updates the current selection with a new seat type
    //     Left or right handed
    // Called by the seat type dropdown
    function updateSeatType(event) {
        let newType = event.target.value;
        let newInfo = [...seatInfo];

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.left = newType;
        }

        setSeatType(newType);
        setSeatInfo(newInfo);
        setUnsaved(true);
    }

    // Updates the current selection with a new seat status
    //     Broken or not broken
    // Called by the seat status dropdown
    function updateSeatBroken(event) {
        let newBroken = event.target.value;
        let newInfo = [...seatInfo];

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.broken = newBroken;
        }

        setBroken(newBroken);
        setSeatInfo(newInfo);
        setUnsaved(true);
    }

    // Updates the label of the seat that has been selected
    // Called by the label TextField that appears when a single seat is selected
    function updateLabel(event) {
        let newLabel = event.target.value;
        let newInfo = [...seatInfo];

        let seat = decodeSelect(selected.values().next().value, newInfo);
        seat.label = newLabel;

        setSeatInfo(newInfo);
        setLabel(newLabel);
        setUnsaved(true);
    }

    // Clears the labels of the current selection
    // Called by the clear labels button
    function clearLabel(event) {
        let newLabel = '';
        let newInfo = [...seatInfo];

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.label = newLabel;
        }

        setSeatInfo(newInfo);
        setLabel(newLabel);
        setUnsaved(true);
    }

    // The automatic label generator
    function autoLabel() {
        // A collection of selected seats
        // Not every row has seats so its a dictionary rather than an array
        // All seats are saved as coordinates of the form seats[row][column]
        let seats = {};

        // Adding the seats in the current selection to the seats object
        for(let seatCoords of selected) {
            let [i, j] = seatCoords.split(' ');

            if(seats[i]) {
                seats[i].push(j);
            } else {
                seats[i] = [j];
            }
        }
        
        // Gettings whether the numbers and rows should be mirrored
        let mirrorNumbers = mirrors.includes("numbers");
        let mirrorRows = mirrors.includes("rows");

        // A sorting function for the rows based on mirrorRows
        function sortRows(firstEl, secondEl) {
            if(mirrorRows) {
                return Number(secondEl) - Number(firstEl);
            } else {
                return Number(firstEl) - Number(secondEl);
            }
        }
        
        // A sorting function for the numbers based on mirrorNumbers
        function sortCols(firstEl, secondEl) {
            if(mirrorNumbers) {
                return Number(secondEl) - Number(firstEl);
            } else {
                return Number(firstEl) - Number(secondEl);
            }
        }

        // Sorted seats will be a 2D array of the seats in the order they should be labelled
        let sortedRows = Object.keys(seats).sort(sortRows);
        let sortedSeats = [];
        for(let i=0; i < sortedRows.length; i++) {
            sortedSeats.push([sortedRows[i], seats[sortedRows[i]].sort(sortCols)]);
        }

        // Now we actually label those seats using the sortedSeats array
        let newInfo = [...seatInfo];
        // We get the number which represents A in ASCII
        // Because we'll automatically generate row letters
        let aCharCode = 'A'.charCodeAt(0);
        for(let i=0; i < sortedSeats.length; i++) {
            let rowNum = sortedSeats[i][0];
            let colNums = sortedSeats[i][1];

            // For every seat in the row
            for(let j=0; j < colNums.length; j++) {
                // Decide on its label based on its position in the sortedSeats array
                let seat = newInfo[rowNum][colNums[j]];
                seat.label = `${String.fromCharCode(aCharCode + i)}${j + 1}`;

                // Also reset the leftness and brokenness of the seat
                // This could be removed, it's more of a personal preference to reset them
                seat.left = false;
                seat.broken = false;
            }
        }

        setSeatInfo(newInfo);
        setUnsaved(true);
    }

    // A mini version of autoLabel but used for a single row
    // See comments on autoLabel for idea of how it works
    function autoRowLabel() {
        let seats = [];
        let row;

        for(let seatCoords of selected) {
            let [i, j] = seatCoords.split(' ');

            row = i;
            seats.push(j);
        }
        
        let mirrorNumbers = mirrors.includes("numbers");
        
        function sortCols(firstEl, secondEl) {
            if(mirrorNumbers) {
                return Number(secondEl) - Number(firstEl);
            } else {
                return Number(firstEl) - Number(secondEl);
            }
        }

        seats.sort(sortCols);

        let newInfo = [...seatInfo];
        for(let i=0; i < seats.length; i++) {
            let seat = newInfo[row][seats[i]];
            seat.label = `${rowLabel}${i + 1}`;
            seat.left = false;
            seat.broken = false;
        }

        setSeatInfo(newInfo);
        setRowLabel('');
        setUnsaved(true);
    }

    // Checks to see whether the selection is of a single row or not
    function selectIsSingleRow() {
        let row = undefined;
        for(let seatCoords of combine(selected, selection)) {
            // eslint-disable-next-line
            let [i, j] = seatCoords.split(' ');

            if(row === undefined) {
                row = i;
            } else if (row !== i) {
                row = null;
            }
        }

        return row;
    }

    // Adds 5 rows to the 2D seatInfo array
    function addRows() {
        let newInfo = [...seatInfo];
        let newRows = 5;

        for(let i=0; i < newRows; i++) {
            let newRow = [];

            for(let j=0; j < cols; j++) {
                newRow.push({label: ""});
            }

            newInfo.push(newRow);
        }

        setSeatInfo(newInfo);
        setRows(rows + newRows);
        setUnsaved(true);
    }

    // Adds 5 columns to the 2D seatInfo array
    function addCols() {
        let newInfo = [...seatInfo];
        let newCols = 5;

        for(let i=0; i < rows; i++) {
            for(let j=0; j < newCols; j++) {
                newInfo[i].push({label: ""});
            }
        }

        setSeatInfo(newInfo);
        setCols(cols + newCols);
        setUnsaved(true);
    }

    // Removes blank seats that aren't spacers between seats
    // Nice if you added too many columns or rows
    function trimWhiteSpace() {
        let rowMin = rows;
        let rowMax = 0;
        let colMin = cols;
        let colMax = 0;

        // First we find what rows and columns are actually being used
        // Here we figure out which seat is the furthest left, right, up, and down
        for(let i=0; i < rows; i++) {
            for(let j=0; j < cols; j++) {
                if(seatInfo[i][j].label) {
                    rowMin = Math.min(i, rowMin);
                    colMin = Math.min(j, colMin);
                    rowMax = Math.max(i, rowMax);
                    colMax = Math.max(j, colMax);
                }
            }
        }

        // Based on the values gotten above we can create a new seatInfo array and populate it
        if(rowMin === rows && rowMax === 0) {
            let newInfo = [];
            let newRows = 10;
            let newCols = 10;

            for(let i=0; i < newRows; i++) {
                let newRow = [];

                for(let j=0; j < newCols; j++) {
                    newRow.push({
                        label: "",
                        left: false,
                        broken: false,
                    });
                }

                newInfo.push(newRow);
            }

            setSeatInfo(newInfo);
            setRows(newRows);
            setCols(newCols);
            return;
        }

        let newInfo = [];
        let newRows = rowMax - rowMin + 1;
        let newCols = colMax - colMin + 1;

        for(let i=rowMin; i <= rowMax; i++) {
            let newRow = []

            for(let j=colMin; j <= colMax; j++) {
                newRow.push(seatInfo[i][j]);
            }

            newInfo.push(newRow);
        }

        setSeatInfo(newInfo);
        setRows(newRows);
        setCols(newCols);
        setUnsaved(true);
    }



    /*
    Save Functions
    */

    // When the unsaved state changes we want to update whether the page
    //     will alert you when you try to leave
    useEffect(() => {
        if(unsaved) {
            window.onbeforeunload = () => "Unsaved work";
        } else {
            window.onbeforeunload = () => null;
        }
    }, [unsaved]);

    // Turns the layouts array into MenuItems
    function layoutsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < layouts.length; i++) {
            menuItems.push(
                <MenuItem value={i} key={layouts[i].id}>{layouts[i].location}</MenuItem>
            );
        }

        return menuItems;
    }

    // Turns the layout into a JSON
    function toJSON() {
        return {
            location: location,
            seats: JSON.stringify(seatInfo),
            count: seatCount
        };
    }

    // If the selected layout changes we want to update a bunch of values
    useEffect(() => {
        if(selectedLayout === '') return;

        let layout = layouts[selectedLayout];

        clearEditorStates();
        
        let newInfo = JSON.parse(layout.seats);
        setLocation(layout.location);
        setSeatInfo(newInfo);

        setRows(newInfo.length);
        setCols(newInfo[0].length);
        setUnsaved(false);
    }, [selectedLayout]); // eslint-disable-line react-hooks/exhaustive-deps
    
    // This finds a value based on location / layout name
    // Useful for when the set of layouts changes
    function findLayout() {
        let layout;
        for(let i=0; i < layouts.length; i++) {
            if(layouts[i].location === location) {
                layout = layouts[i];
            }
        }

        return layout;
    }

    // This saves the layout to the database
    function saveLayout() {
        let layout = findLayout();

        let func;
        if(layout) {
            func = server.updateLayout;
        } else {
            func = server.addLayout;
        }

        func(toJSON())
            .then((response) => {
                updateLayouts();
            })
            .catch((err) => {
                console.error(err);
            });
        
        setUnsaved(false);
    }

    // When the sets of layouts changes
    // We an't use the findLayout function because it hasn't technically updated yet?
    useEffect(() => {
        let oldLayout;
        for(let i=0; i < props.layouts.length; i++) {
            if(props.layouts[i].location === location) {
                oldLayout = i;
                break;
            }
        }
        if(oldLayout) {
            setSelectedLayout(oldLayout);
        }
    }, [props.layouts]); // eslint-disable-line react-hooks/exhaustive-deps


    // If passed a hidden prop, return null
    if(props.hidden) {
        return null;
    }

    return (
        <div className={classes.editorMain}>
            {hasError && <Alert severity="error">Current layout has seats with duplicate labels!</Alert>}

            {/* The save system that contains the load dropdown and saving TextField and Button */}
            <Grid container id="save-system" spacing={2} wrap="nowrap">
                {/* Loading dropdown */}
                <Grid item xs={4}>
                    <TextField select
                        label="Load"
                        value={selectedLayout}
                        onChange={(e) => setSelectedLayout(e.target.value)}
                    >
                        {/* The MenuItems are generated dynamically with this function */}
                        {layoutsToMenuItems()}
                    </TextField>
                </Grid>

                {/* Layout name / Location TextField */}
                <Grid item xs={4}>
                    <TextField label="Name" value={location} onChange={(e) => setLocation(e.target.value)}/>
                </Grid>

                {/* Save button + unsaved work alert */}
                <Grid container spacing={2} item xs wrap="nowrap">
                    <Grid item>
                        <Button variant="contained" onClick={saveLayout} disabled={hasError}>{findLayout() ? "Update" : "Save"}</Button>
                    </Grid>
                    <Grid item>
                        {unsaved && <Alert severity="warning">Unsaved work</Alert>}
                    </Grid>
                </Grid>
            </Grid>
            <br />

            {/* The seat display */}
            <SeatLayout
                rows={rows} cols={cols} assignment={false}
                seatInfo={seatInfo}
                handleMouseDown={handleMouseDown}
                handleMouseUp={handleMouseUp}
                handleMouseOver={handleMouseOver}
                selected={combine(selected, selection)}
            />
            <br />

            {/* The editor elements */}
            <Grid container id="editor" spacing={2} wrap="nowrap">
                {/* First we have the labelling */}
                <Grid container item xs spacing={2}>

                    {/* Depending on how many seats are selected we change what's displayed using the ternary operator */}
                    {combine(selected, selection).size > 1 ?

                    // If more than one seat is selected
                    <Grid container item direction="column">

                        {!selectIsSingleRow() ?
                        // If more than a single row is selected
                        <React.Fragment>
                            {/* Auto Label button */}
                            <Grid item>
                                <InputLabel id="autolabel-label">Auto Label</InputLabel>
                                <Button variant="contained" onClick={autoLabel}>Auto Label</Button>
                            </Grid>

                            {/* The Mirroring toggle buttons */}
                            <Grid item>
                                <InputLabel id="mirror-label">Reflect</InputLabel>
                                <ToggleButtonGroup value={mirrors} onChange={(e, m) => setMirrors(m)}>
                                    <ToggleButton value="numbers">
                                        Numbers
                                    </ToggleButton>
                                    <ToggleButton value="rows">
                                        Rows
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Grid>

                        </React.Fragment>
                        :
                        // If only a single row is selected
                        <React.Fragment>
                            {/* Auto Label button, but hooked up to the autoRowLabel function */}
                            <Grid item>
                                <InputLabel id="autolabel-label">Auto Label</InputLabel>
                                <Button variant="contained" onClick={autoRowLabel}>Auto Label</Button>
                            </Grid>

                            {/* A TextField to change the row label */}
                            <Grid item>
                                <TextField label="Row Label" value={rowLabel} onChange={(e) => setRowLabel(e.target.value)}/>
                            </Grid>

                            {/* The Mirror Numbers toggle button */}
                            <Grid item>
                                <InputLabel id="mirror-label">Reflect</InputLabel>
                                <ToggleButtonGroup value={mirrors} onChange={(e, m) => setMirrors(m)}>
                                    <ToggleButton value="numbers">
                                        Numbers
                                    </ToggleButton>
                                </ToggleButtonGroup>
                            </Grid>

                        </React.Fragment>
                        }
                    </Grid>

                    :
                    // If only a single seat is selected
                    <Grid item>
                        <TextField label="Label" value={label} onChange={updateLabel}/>
                    </Grid>
                    }
                </Grid>
                {/* End of the labelling set of elements */}

                {/* Clear Label Button */}
                <Grid item xs>
                    <Button variant="contained" onClick={clearLabel}>Clear Label</Button>
                </Grid>

                {/* Dropdowns for seat type and state */}
                <Grid container item direction="column" xs>

                    {/* Seat Type dropdown */}
                    <Grid item>
                        <TextField select
                            label="Seat Type"
                            value={seatType}
                            onChange={updateSeatType}
                        >
                            <MenuItem value={true}>Left-Handed</MenuItem>
                            <MenuItem value={false}>Right-Handed</MenuItem>
                        </TextField>
                    </Grid>

                    {/* Seat State dropdown */}
                    <Grid item>
                        <TextField select
                            label="Seat Status"
                            value={broken}
                            onChange={updateSeatBroken}
                        >
                            <MenuItem value={true}>Broken</MenuItem>
                            <MenuItem value={false}>Not Broken</MenuItem>
                        </TextField>
                    </Grid>
                </Grid>

                {/* Buttons for adding more rows and columns and trimming white space */}
                <Grid container item direction="column" xs>
                    <Grid item>
                        <Button variant="contained" onClick={addRows}>Add Rows</Button>
                    </Grid>
                    <Grid item>
                        <Button variant="contained" onClick={addCols}>Add Columns</Button>
                    </Grid>
                    <Grid item>
                        <Button variant="contained" onClick={trimWhiteSpace}>Trim White Space</Button>
                    </Grid>
                </Grid>
            </Grid>
        </div>
    );
}

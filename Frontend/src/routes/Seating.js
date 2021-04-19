import OurTheme from "../style/Theme";
import Styles from "../style/SeatingStyle";
import { ThemeProvider } from "@material-ui/styles";
import { Grid, TextField, MenuItem, Button, InputLabel } from "@material-ui/core";
import { ToggleButton, ToggleButtonGroup } from '@material-ui/lab';
import React, { useState } from "react";
import SeatLayout from "../components/SeatLayout";

let initSeatInfo = [];
for(let i=0; i < 15; i++) {
    initSeatInfo.push([]);
    for(let j=0; j < 15; j++) {
        initSeatInfo[i].push({label:""});
    }
}

let mouseDownCoords = null;
let invertSelection = false;

export default function Seating() {
    const classes = Styles.useStyles();
    const theme = OurTheme.theme;

    const [seatInfo, setSeatInfo] = useState(initSeatInfo);
    const [rows, setRows] = useState(15);
    const [cols, setCols] = useState(15);
    // eslint-disable-next-line
    const [assignment, setAssignment] = useState(undefined);
    const [selected, setSelected] = useState(new Set());
    const [selection, setSelection] = useState(new Set());
    const [seatType, setSeatType] = useState('');
    const [broken, setBroken] = useState('');
    const [label, setLabel] = useState('');
    const [rowLabel, setRowLabel] = useState('');
    const [mirrors, setMirrors] = useState([]);

    function handleMouseDown(event, i, j) {
        mouseDownCoords = [i,j];
        let newSelection = new Set();
        newSelection.add(`${i} ${j}`);

        if(event.ctrlKey) {
            invertSelection = true;
        } else if(!event.shiftKey) {
            let newSelected = new Set();
            setSelected(newSelected);
        }

        setSelection(newSelection);
}

    function handleMouseUp(event, i, j) {
        if(mouseDownCoords == null) {
            return;
        }

        let newSelected = combine(selected, selection);
        let newSelection = new Set();
        
        setSelected(newSelected);
        setSelection(newSelection);
        mouseDownCoords = null;

        let newType = undefined;
        let newBroken = undefined;
        let newLabel = undefined;
        for(let seatCoords of newSelected) {
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

        invertSelection = false;
        setSeatType(newType);
        setBroken(newBroken);
        setLabel(newLabel);
    }

    function handleMouseOver(i, j) {
        if(mouseDownCoords == null) {
            return;
        }

        let newSelection = new Set();

        let iMin = Math.min(mouseDownCoords[0], i);
        let jMin = Math.min(mouseDownCoords[1], j);
        let iMax = Math.max(mouseDownCoords[0], i);
        let jMax = Math.max(mouseDownCoords[1], j);

        for(let k=iMin; k <= iMax; k++) {
            for(let l=jMin; l <= jMax; l++) {
                newSelection.add(`${k} ${l}`);
            }
        }

        setSelection(newSelection);
    }

    function combine(newSelected, newSelection) {
        let toReturn = new Set();

        for(let item of newSelected) {
            toReturn.add(item);
        }

        if(invertSelection) {
            for(let item of newSelection) {
                if(newSelected.has(item)) {
                    toReturn.delete(item);
                } else {
                    toReturn.add(item);
                }
            }
        } else {
            for(let item of newSelection) {
                toReturn.add(item);
            }
        }

        return toReturn;
    }

    function decodeSelect(selectItem, arr) {
        let [i, j] = selectItem.split(' ');
        arr = arr || seatInfo;
        return arr[i][j];
    }

    function updateSeatType(event) {
        let newType = event.target.value;
        let newInfo = [...seatInfo];

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.left = newType;
        }

        setSeatType(newType);
        setSeatInfo(newInfo);
    }
    
    function updateSeatBroken(event) {
        let newBroken = event.target.value;
        let newInfo = [...seatInfo];

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.broken = newBroken;
        }

        setBroken(newBroken);
        setSeatInfo(newInfo);
    }

    function updateLabel(event) {
        let newLabel = event.target.value;
        let newInfo = [...seatInfo];

        let seat = decodeSelect(selected.values().next().value, newInfo);
        seat.label = newLabel;

        setSeatInfo(newInfo);
        setLabel(newLabel);
    }

    function clearLabel(event) {
        let newLabel = '';
        let newInfo = [...seatInfo];

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.label = newLabel;
        }

        setSeatInfo(newInfo);
        setLabel(newLabel);
    }

    function autoLabel() {
        let seats = {};

        for(let seatCoords of selected) {
            let [i, j] = seatCoords.split(' ');

            if(seats[i]) {
                seats[i].push(j);
            } else {
                seats[i] = [j];
            }
        }
        
        let mirrorNumbers = mirrors.includes("numbers");
        let mirrorRows = mirrors.includes("rows");

        function sortRows(firstEl, secondEl) {
            if(mirrorRows) {
                return Number(secondEl) - Number(firstEl);
            } else {
                return Number(firstEl) - Number(secondEl);
            }
        }
        
        function sortCols(firstEl, secondEl) {
            if(mirrorNumbers) {
                return Number(secondEl) - Number(firstEl);
            } else {
                return Number(firstEl) - Number(secondEl);
            }
        }

        let sortedRows = Object.keys(seats).sort(sortRows);
        let sortedSeats = [];
        for(let i=0; i < sortedRows.length; i++) {
            sortedSeats.push([sortedRows[i], seats[sortedRows[i]].sort(sortCols)]);
        }


        let newInfo = [...seatInfo];
        let aCharCode = 'A'.charCodeAt(0);
        for(let i=0; i < sortedSeats.length; i++) {
            let rowNum = sortedSeats[i][0];
            let colNums = sortedSeats[i][1];

            for(let j=0; j < colNums.length; j++) {
                let seat = newInfo[rowNum][colNums[j]];
                seat.label = `${String.fromCharCode(aCharCode + i)}${j + 1}`;
                seat.left = false;
                seat.broken = false;
            }
        }

        setSeatInfo(newInfo);
    }

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
    }

    function selectedIsSingleRow() {
        let row = undefined;
        for(let seatCoords of selected) {
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
    }

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
    }

    function trimWhiteSpace() {
        let rowMin = rows;
        let rowMax = 0;
        let colMin = cols;
        let colMax = 0;

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
    }

    function markDuplicates(oldInfo) {
        let info = [...oldInfo];
        let seatLabels = {};

        for(let i=0; i < rows; i++) {
            for(let j=0; j < cols; j++) {
                let seatLabel = info[i][j].label;
                info[i][j].error = false;

                if(seatLabel === '') {
                    continue;
                } else if(seatLabels[seatLabel] !== undefined) {
                    seatLabels[seatLabel].push([i, j]);

                    for(let k=0; k < seatLabels[seatLabel].length; k++) {
                        let [x, y] = seatLabels[seatLabel][k];
                        info[x][y].error = true;
                    }
                } else {
                    seatLabels[seatLabel] = [[i, j]];
                }
            }
        }

        return info;
    }

    return (
        <div className={classes.root}>
            <ThemeProvider theme={theme}>
                <Grid container id="save-system" spacing={2}>
                    <Grid item xs>
                        <TextField select
                            label="Layout"
                        >
                            <MenuItem>Option 1</MenuItem>
                        </TextField>
                    </Grid>
                    <Grid item xs>
                        <Button variant="contained">Load</Button>
                    </Grid>
                    <Grid item xs>
                        <TextField label="Name"/>
                    </Grid>
                    <Grid item xs>
                        <Button variant="contained">Save</Button>
                    </Grid>
                </Grid>
                <br></br>
                <SeatLayout
                  rows={rows} cols={cols} assignment={assignment}
                  seatInfo={markDuplicates(seatInfo)}
                  handleMouseDown={handleMouseDown}
                  handleMouseUp={handleMouseUp}
                  handleMouseOver={handleMouseOver}
                  selected={combine(selected, selection)}
                />
                <br></br>
                <Grid container id="editor" spacing={2}>
                    <Grid container item direction="column" xs>
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
                    <Grid container item xs spacing={2}>
                        {selected.size > 1 ?
                        <Grid container item direction="column">
                            {!selectedIsSingleRow() ?
                            <React.Fragment>
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
                                <Grid item>
                                    <InputLabel id="autolabel-label">Auto Label</InputLabel>
                                    <Button variant="contained" onClick={autoLabel}>Auto Label</Button>
                                </Grid>
                            </React.Fragment>
                            :
                            <React.Fragment>
                                <Grid container item spacing={2}>
                                    <Grid item>
                                        <InputLabel id="mirror-label">Reflect</InputLabel>
                                        <ToggleButtonGroup value={mirrors} onChange={(e, m) => setMirrors(m)}>
                                            <ToggleButton value="numbers">
                                                Numbers
                                            </ToggleButton>
                                        </ToggleButtonGroup>
                                    </Grid>
                                    <Grid item>
                                        <TextField label="Row Label" value={rowLabel} onChange={(e) => setRowLabel(e.target.value)}/>
                                    </Grid>
                                </Grid>
                                <Grid item>
                                    <InputLabel id="autolabel-label">Auto Label</InputLabel>
                                    <Button variant="contained" onClick={autoRowLabel}>Auto Label</Button>
                                </Grid>
                            </React.Fragment>
                            }
                        </Grid>
                        :
                        <Grid item>
                            <TextField label="Label" value={label} onChange={updateLabel}/>
                        </Grid>
                        }
                    </Grid>
                    <Grid item xs>
                        <Button variant="contained" onClick={clearLabel}>Clear Label</Button>
                    </Grid>
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
            </ThemeProvider>
        </div>
    );
}

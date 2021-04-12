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
    for(let j=0; j < 7; j++) {
        initSeatInfo[i].push({
            label: `${String.fromCharCode('A'.charCodeAt(0) + i)}${j}`,
            left: j === 14,
            broken: i === 14 && j === 14,
        });
    }
    initSeatInfo[i].push({
        label: ``,
    });
    for(let j=8; j < 15; j++) {
        initSeatInfo[i].push({
            label: `${String.fromCharCode('A'.charCodeAt(0) + i)}${j}`,
            left: j === 14,
            broken: i === 14 && j === 14,
        });
    }
}

let initAssignment = {};
for(let i=0; i < 15; i++) {
    for(let j=0; j < 15; j++) {
        if(j%2 === 0 && !initSeatInfo[i][j].broken) {
            initAssignment[`${String.fromCharCode('A'.charCodeAt(0) + i)}${j}`] = true;
        }
    }
}

let mouseDownCoords = null;
let invertSelection = false;

export default function Seating() {
    const classes = Styles.useStyles();
    const theme = OurTheme.theme;

    const [seatInfo, setSeatInfo] = useState(initSeatInfo);
    // eslint-disable-next-line
    const [rows, setRows] = useState(15);
    // eslint-disable-next-line
    const [cols, setCols] = useState(15);
    // eslint-disable-next-line
    const [assignment, setAssignment] = useState(undefined);
    const [selected, setSelected] = useState(new Set());
    const [selection, setSelection] = useState(new Set());
    const [seatType, setSeatType] = useState('');
    const [broken, setBroken] = useState('');
    const [label, setLabel] = useState('');
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

        let newType = null;
        let newBroken = null;
        let newLabel = null;
        for(let seatCoords of newSelected) {
            let seat = decodeSelect(seatCoords);

            if(newLabel === null) {
                newLabel = seat.label;
            }

            if(newType === null) {
                newType = seat.left;
            } else if (seat.left !== newType) {
                newType = '';
            }

            if(newBroken === null) {
                newBroken = seat.broken;
            } else if (seat.broken !== newBroken) {
                newBroken = '';
            }
        }

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
        let newInfo = Object.assign({}, seatInfo);

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.left = newType;
        }

        setSeatType(newType);
        setSeatInfo(newInfo);
    }
    
    function updateSeatBroken(event) {
        let newBroken = event.target.value;
        let newInfo = Object.assign({}, seatInfo);

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.broken = newBroken;
        }

        setBroken(newBroken);
        setSeatInfo(newInfo);
    }

    function updateLabel(event) {
        let newLabel = event.target.value;
        let newInfo = Object.assign({}, seatInfo);

        let seat = decodeSelect(selected.values().next().value, newInfo);
        seat.label = newLabel;

        setSeatInfo(newInfo);
        setLabel(newLabel);
    }

    function clearLabel(event) {
        let newLabel = '';
        let newInfo = Object.assign({}, seatInfo);

        for(let seatCoords of selected) {
            let seat = decodeSelect(seatCoords, newInfo);
            seat.label = newLabel;
        }

        setSeatInfo(newInfo);
        setLabel(newLabel);
    }

    function autoLabel() {
        console.log('autoLabel')
    }

    return (
        <div className={classes.root}>
            <ThemeProvider theme={theme}>
                <SeatLayout
                  rows={rows} cols={cols} assignment={assignment}
                  seatInfo={seatInfo}
                  handleMouseDown={handleMouseDown}
                  handleMouseUp={handleMouseUp}
                  handleMouseOver={handleMouseOver}
                  selected={combine(selected, selection)}
                ></SeatLayout>
                <br></br>
                <Grid container id={'editor'} spacing={2}>
                    <Grid item xs>
                        <TextField select
                            label={'Seat Type'}
                            value={seatType}
                            onChange={updateSeatType}
                        >
                            <MenuItem value={true}>Left-Handed</MenuItem>
                            <MenuItem value={false}>Right-Handed</MenuItem>
                        </TextField>
                    </Grid>
                    <Grid item xs>
                        <TextField select
                            label={'Seat Status'}
                            value={broken}
                            onChange={updateSeatBroken}
                        >
                            <MenuItem value={true}>Broken</MenuItem>
                            <MenuItem value={false}>Not Broken</MenuItem>
                        </TextField>
                    </Grid>
                    <Grid container item xs={6} spacing={2}>
                        {selected.size > 1 ?
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
                        <Grid item>
                            <TextField label="Label" value={label} onChange={updateLabel}/>
                        </Grid>
                        }
                        <Grid item>
                            <Button variant="contained" onClick={clearLabel}>Clear Label</Button>
                        </Grid>
                    </Grid>
                </Grid>
            </ThemeProvider>
        </div>
    );
}

import Styles from "../style/SeatingStyle";
import { Box } from "@material-ui/core";
import React from "react";

export default function SeatLayout(props) {
    const classes = Styles.useStyles();

    // If these props aren't specified we want them to have a reasonable default
    // The handle functions are callbacks for when a mouse action occurs on a seat box
    let handleMouseDown = props.handleMouseDown !== undefined ? props.handleMouseDown : () => {};
    let handleMouseUp = props.handleMouseUp !== undefined ? props.handleMouseUp : () => {};
    let handleMouseOver = props.handleMouseOver !== undefined ? props.handleMouseOver : () => {};
    // selected is a set of seat boxes which are currently highlighted
    let selected = props.selected !== undefined ? props.selected : new Set();

    // 2D array we'll put all the seats in
    let seats2D = [];
    for(let i=0; i < props.rows; i++) {
        // A single row of the 2D array
        let row = [];

        for(let j=0; j < props.cols; j++) {
            // Retreive information about the seat from the seatInfo prop
            let seatInfo = props.seatInfo[i][j];

            // The classes given to the seat is how we choose which CSS effects are used
            let className = ` ${classes.seat}`;

            // The seat layout has two modes: assignment, and layout
            // Layout is for editting the seats, you can highlight seats that have been selected
            //     and see properties like whether they're left handed easily
            // Assignment is for use when students have been assigned to seats. You can easily 
            //     see which seats are meant to be filled and which ones are meant to be empty
            // To differentiate between the two modes you pass a seat assignment dictionary
            //     or you don't pass it
            if(props.assignment) {
                if(!seatInfo.label) {
                    className += ` ${classes.assignBlank}`;
                } else {
                    className += ` ${classes.assignSeat}`;
                    
                    if(props.assignment[seatInfo.label]) {
                        className += ` ${classes.assignFilled}`;
                    } else {
                        className += ` ${classes.assignEmpty}`;
                    }
                }
            } else {
                className += ` ${selected.has(`${i} ${j}`) ? classes.layoutSelected : classes.layoutUnselected}`;

                if(seatInfo.error) {
                    className += ` ${classes.layoutError}`;
                } else if(!seatInfo.label) {
                    className += ` ${classes.layoutBlank}`;
                } else if(seatInfo.broken) {
                    className += ` ${classes.layoutBroken}`;
                } else if(seatInfo.left) {
                    className += ` ${classes.layoutLeftSeat}`;
                } else {
                    className += ` ${classes.layoutSeat}`;
                }
            }

            // This is a single seat in the 2D array
            row.push(
                <Box
                    id={`${i},${j}`}
                    key={`${seatInfo.label} ${i} ${j}`}
                    className={className}
                    onMouseDown={(event) => handleMouseDown(event, i, j)}
                    onMouseUp={(event) => handleMouseUp(event, i, j)}
                    onMouseOver={(event) => handleMouseOver(i,j)}
                >
                    {seatInfo.label}
                </Box>
            );
        }

        // We use an inline-flex flexbox for the rows because we don't want
        //     the row to take 100% width, but rather wrap the elements inside it
        seats2D.push(
            <div style={{display: "inline-flex", flexWrap:"nowrap"}} key={i}>
                {row}
            </div>
        );
    }

    // If the seat layout is passed a hidden prop, return null
    if(props.hidden) {
        return null;
    }
    
    return (
        <div id="seats" style={{display: "inline-flex", flexFlow: "column nowrap"}}>
            <div className={classes.frontBanner}>Front</div>
            {seats2D}
            <div className={classes.frontBanner}>Back</div>
        </div>
    )
}

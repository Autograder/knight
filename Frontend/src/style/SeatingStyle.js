import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
    root : {
        position : 'absolute',
        width : '100%',
        left: 0,
        right: 0,
        backgroundColor: "darkgrey",
        
    },
    '@global': {
        '.MuiFormControl-root': {
            width: "100%",
        },
        '#menu- .MuiPaper-root': {
            color: "black",
        },
    },
    seat: {
        height: "2em",
        width: "2em",
        textAlign: "center",
        lineHeight: "2em",
        userSelect: "none",
        MozUserSelect: "none",
        WebkitUserSelect: "none",
        msUserSelect: "none",
    },
    assignSeat: {
        borderRadius: "5px",
        margin: "3px",
        border: "1px solid black",
    },
    assignFilled: {
        backgroundColor: "lightgreen",
    },
    assignEmpty: {
        backgroundColor: "indianred",
    },
    assignBlank: {
        backgroundColor: "rgba(0,0,0,0)",
        margin: "4px",
    },
    layoutSeat: {
        backgroundColor: "white",
    },
    layoutError: {
        backgroundColor: "red",
    },
    layoutLeftSeat: {
        backgroundColor: "yellow",
    },
    layoutBroken: {
        backgroundColor: "grey",
    },
    layoutBlank: {
        backgroundColor: "darkgrey",
    },
    layoutSelected: {
        border: "4px solid black",
    },
    layoutUnselected: {
        border: "1px solid black",
        padding: "3px",

    }
}));

const e = {useStyles};
export default e;
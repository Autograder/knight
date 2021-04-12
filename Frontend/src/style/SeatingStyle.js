import { makeStyles } from '@material-ui/core/styles';
import { black } from 'material-ui/styles/colors';

const useStyles = makeStyles((theme) => ({
    root : {
        position : 'absolute',
        width : '100%',
        left: 0,
        right: 0,
        color: black,
    },
    '@global': {
        '#editor .MuiFormControl-root': {
            width: "100%",
        },
    },
    seat: {
        height: "40px",
        width: "40px",
        textAlign: "center",
        lineHeight: "40px",
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
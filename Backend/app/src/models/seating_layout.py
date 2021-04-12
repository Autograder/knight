# needed for annotating return types of the same object
from __future__ import annotations

from typing import Dict, Tuple, Optional, List

from ...setup import db


class SeatingLayout(db.Model):
    """
    Represents a layout of seats in the DB with relevant functions for
    manipulation of that data.\n
    Fields:
    id --> Seating Arrangment ID. Unique, primary key\n
    location --> The location the seating layout represents. Unique.\n
    seats --> A JSON string for the 2D seat array.\n
    count --> Total seat count.\n
    @author: james-c-lars
    """
    __tablename__ = 'SeatingLayouts'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    location = db.Column(db.String(255), unique=True, nullable=False)
    seats = db.Column(db.Text, nullable=True)
    count = db.Column(db.Integer, nullable=True)

    def __repr__(self) -> str:
        """
        Returns a String representing the location
        """
        return self.location

    def save(self) -> None:
        '''
        Saves the current object in the DB.\n
        Params: None\n
        Returns: None
        '''
        db.session.commit()

    def to_json(self) -> Dict[str, str]:
        '''
        Function that takes a user object and returns it in dictionary
        form. Used on the API layer.\n
        Params: none\n
        Returns: Dictionary of the user info
        '''
        ret = {}
        ret['id'] = self.id
        ret['location'] = self.location
        ret['seats'] = self.seats
        ret['count'] = self.count
        return ret

    @staticmethod
    def create_layout(location: str, seats: str,
                      count: int) -> Tuple[bool, SeatingLayout]:
        '''
        Function that creates a new seating layout object and adds it to
        the database.\n
        Params: location - string. Where the seating location is.\n
        seats - str. The 2D seat list.\n
        count - int. The total number of seats in the layout.\n
        Returns: boolean value for whether the location already existed,
        and a SeatingArrangment object if the creation was successful.
        '''

        # don't try to add a preexisting layout
        if SeatingLayout.find_by_location(location):
            return False, None

        sa = SeatingLayout(location=location, seats=seats,
                           count=count)
        db.session.add(sa)
        sa.save()
        return True, sa

    @staticmethod
    def find_by_location(location: str) -> Optional[SeatingLayout]:
        '''
        Function that tries to find a seating layout via the location it
        is in.

        Note that this function may return `None` if the given location
        doesn't map to any known seating layouts.\n
        Params: location - string.\n
        Returns: Optional[SeatingLayout]
        '''
        return SeatingLayout.query.filter_by(location=location).first()

    @staticmethod
    def find_by_id(layout_id: db.Integer) -> Optional[SeatingLayout]:
        '''
        Function that retrieves an layout via the id.\n
        Params: `layout_id` - layout ID in the DB.\n
        Returns: Optional[SeatingLayout]
        '''
        return SeatingLayout.query.filter_by(id=layout_id).first()

    @staticmethod
    def get_all_layouts() -> List[SeatingLayout]:
        '''
        Function that returns a list of all layouts in the database.\n
        Params: None\n
        Returns: List[SeatingLayout]
        '''
        return SeatingLayout.query.all()

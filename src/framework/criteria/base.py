from pydantic import BaseModel


class BaseCriterion(BaseModel):
    """
    Base class for all criteria.
    """

    value: str

    def evaluate(self, *args, **kwargs) -> float:
        """
        Evaluate the criterion.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            float: The evaluation value.
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> float:
        """
        Evaluate the criterion.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            float: The evaluation value.
        """
        return self.evaluate(*args, **kwargs)
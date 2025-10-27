from functools import reduce  # Used for operations like product
from collections import Counter   # Used for counting occurrences (for mode calculation)

# Raised when a value of an invalid data type is added to the DynamicList
class InvalidElementTypeError(TypeError):
    pass

# Raised when two DynamicList objects of different types (e.g., int vs str) are compared or combined
class WrongDataTypeError(TypeError):
    pass

# Raised when an operation requiring data (like mean or sum) is called on an empty DynamicList
class EmptyListError(Exception):
    pass

# Raised when trying to access or modify an index that does not exist in the DynamicList
class IndexOutOfRangeError(IndexError):
    pass

# Raised when performing element-wise operations on lists of different lengths
class LengthNotEqualError(Exception):
    pass

# Raised when an unexpected or invalid value is provided (e.g., percentile not in 0–100 range)
class UnknownValueError(Exception):
    pass


class DynamicList:
    """A flexible list class that enforces data type constraints and adds extra functionality."""

    def __init__(self, allowed_type=(int, float)):
        """
        Initialize a DynamicList with optional type restriction.
        
        Args:
            allowed_type (tuple): Allowed data types for list elements.
        """
        self.__data = []                    # Internal list storage
        self.__allowed_type = allowed_type  # Permitted data types

    def __str__(self):
        """Return a user-friendly string representation."""
        return f'{self.__data}'

    def __repr__(self):
        """Return a detailed representation for debugging."""
        return f"DynamicList({self.__data!r}, allowed_type={self.__allowed_type})"

    def __validate_type(self, value, allowed_type=None):
        """
        Ensure the given value matches the allowed data type(s).
        
        Args:
            value: Item to check.
            allowed_type: Custom type override (defaults to instance allowed_type).
        """
        if allowed_type is None:
            allowed_type = self.__allowed_type
        if not isinstance(value, allowed_type):
            raise InvalidElementTypeError(
                f"This list only accepts types {allowed_type}, but got {type(value).__name__}."
            )

    def __validate_other(self, other):
        """Check that the other object is also a DynamicList."""
        if not isinstance(other, DynamicList):
            raise WrongDataTypeError('Both Lists must be of the same Data Type.')

    def __validate_empty_list(self):
        """Ensure the list is not empty before performing certain operations."""
        if len(self.__data) == 0:
            raise EmptyListError('Cannot perform operation on an empty DynamicList.')

    def __validate_index_error(self, index):
        """Verify that the given index is within valid range."""
        if index >= len(self.__data) or index < -len(self.__data):
            raise IndexOutOfRangeError('DynamicList index out of range.')

    def __validate_contents_are_numeric(self):
        """
        Confirm that all list elements are numeric (int or float).
        Used before statistical calculations.
        """
        self.__validate_empty_list()
        numeric_types = (int, float)

        allowed = self.__allowed_type if isinstance(self.__allowed_type, tuple) else (self.__allowed_type,)
        for t in allowed:
            if not issubclass(t, numeric_types):
                raise WrongDataTypeError(
                    f"Statistical methods require numeric types, but this list allows {t.__name__}."
                )

    def append(self, value):
        """
        Add a single value to the end of the DynamicList.
        
        Args:
            value: The element to append.
        """
        self.__validate_type(value)  # Ensure value matches allowed type
        self.__data.append(value)

    def insert(self, index, value):
        """
        Insert a value at a specific index.
        
        Args:
            index: Position to insert at.
            value: The element to insert.
        """
        if index > len(self.__data) or index < -len(self.__data):
            raise IndexOutOfRangeError('DynamicList index not found.')
        self.__validate_type(value)
        self.__data.insert(index, value)

    def extend(self, l):
        """
        Extend the DynamicList by appending elements from another iterable.
        
        Args:
            l: Iterable containing elements to add.
        """
        for i in l:
            self.__validate_type(i)
            self.__data.append(i)

    def pop(self, index=-1):
        """
        Remove and return an element at the given index (default: last item).
        
        Args:
            index: Index of the item to remove (default is -1).
        """
        self.__validate_index_error(index)
        return self.__data.pop(index)
        
    def clear(self):
        """Remove all elements from the DynamicList."""
        self.__data = []  # Reset list to empty

    def reverse(self):
        """
        Return a new DynamicList with elements in reverse order.
        
        Returns:
            DynamicList: A reversed copy of the list.
        """
        reversed_data = list(reversed(self.__data))
        return DynamicList.from_list(reversed_data, self.__allowed_type)

    def sort(self, reverse=False):
        """
        Sort the DynamicList in ascending or descending order (in-place).
        
        Args:
            reverse (bool): If True, sort in descending order.
        """
        self.__data = sorted(self.__data, reverse=reverse)

    def count(self, value):
        """
        Count the number of occurrences of a value.
        
        Args:
            value: The element to count.
        Returns:
            int: Number of times the value appears.
        """
        count = 0
        for i in self.__data:
            if i == value:
                count += 1
        return count

    def unique(self):
        """
        Return a new DynamicList with only unique elements (preserves order).
        
        Returns:
            DynamicList: A new list containing distinct values.
        """
        unique_list = []
        for i in self.__data:
            if i not in unique_list:
                unique_list.append(i)
        return DynamicList.from_list(unique_list, self.__allowed_type)

    def index(self, value):
        """
        Return the index of the first occurrence of a value.
        
        Args:
            value: Element to find.
        Returns:
            int: Index of the element.
        Raises:
            UnknownValueError: If the value is not found.
        """
        for i, v in enumerate(self.__data):
            if v == value:
                return i
        raise UnknownValueError(f'{value} not found in DynamicList.')

    def __len__(self):
        """Return the number of elements in the DynamicList."""
        return len(self.__data)

    def __getitem__(self, index):
        """
        Retrieve an item or slice from the DynamicList.
        
        Args:
            index (int or slice): Position or range to access.
        Returns:
            Element or DynamicList: A single element if index is int, 
            or a new DynamicList if index is a slice.
        Raises:
            TypeError: If index is not an int or slice.
        """
        if isinstance(index, slice):
            sliced_data = self.__data[index]
            return DynamicList.from_list(sliced_data, self.__allowed_type)
        elif isinstance(index, int):
            return self.__data[index]
        else:
            raise TypeError(f"List indices must be integers or slices, not {type(index).__name__}")

    def __setitem__(self, index, value):
        """
        Replace an element at a specific index.
        
        Args:
            index (int): Position to modify.
            value: New value to assign.
        Raises:
            InvalidElementTypeError: If the value type is not allowed.
        """
        self.__validate_type(value)
        self.__data[index] = value

    def __delitem__(self, index):
        """
        Delete an element at the given index.
        
        Args:
            index (int): Position to delete.
        Raises:
            IndexOutOfRangeError: If index is out of range.
        """
        self.__validate_index_error(index)
        del self.__data[index]

    def __iter__(self):
        """Return an iterator over the DynamicList."""
        return iter(self.__data)

    def __contains__(self, item):
        """Return True if the item exists in the DynamicList."""
        return item in self.__data

    def __eq__(self, other):
        """
        Compare two DynamicLists for equality.
        
        Args:
            other (DynamicList): Another DynamicList instance.
        Returns:
            bool: True if both lists have same type and contents.
        Raises:
            WrongDataTypeError: If compared with non-DynamicList or mismatched allowed_type.
        """
        self.__validate_other(other)
        if self.__allowed_type != other.__allowed_type:
            raise WrongDataTypeError("Both DynamicLists must have same allowed_type for comparison.")
        return self.__data == other.__data

    def __ne__(self, other):
        """
        Check if two DynamicLists are not equal.
        
        Args:
            other (DynamicList): Another DynamicList instance.
        Returns:
            bool: True if lists differ in content or type.
        """
        self.__validate_other(other)
        return not self.__eq__(other)

    def __lt__(self, other):
        """
        Compare if this DynamicList is less than another.
        Uses Python’s built-in list comparison.
        """
        self.__validate_other(other)
        return self.__data < other.__data

    def __le__(self, other):
        """
        Check if this DynamicList is less than or equal to another.
        """
        self.__validate_other(other)
        return self.__data <= other.__data

    def __gt__(self, other):
        """
        Compare if this DynamicList is greater than another.
        """
        self.__validate_other(other)
        return self.__data > other.__data

    def __ge__(self, other):
        """
        Check if this DynamicList is greater than or equal to another.
        """
        self.__validate_other(other)
        return self.__data >= other.__data

    def __add__(self, other):
        """
        Perform element-wise addition between two DynamicLists.
        
        Args:
            other (DynamicList): Another DynamicList with the same length.
        Returns:
            DynamicList: A new list with summed elements.
        Raises:
            WrongDataTypeError: If 'other' is not a DynamicList.
            LengthNotEqualError: If both lists are not the same size.
        """
        self.__validate_other(other)
        if len(self.__data) != len(other.__data):
            raise LengthNotEqualError('Both Dynamic Lists must be of equal length.')

        # Add corresponding elements and build a new list
        new_list = [self.__data[i] + other.__data[i] for i in range(len(self.__data))]
        return DynamicList.from_list(new_list, self.__allowed_type)

    def __sub__(self, other):
        """
        Perform element-wise subtraction between two DynamicLists.

        Args:
            other (DynamicList): Another DynamicList with equal length.
        Returns:
            DynamicList: A new list with element-wise differences.
        Raises:
            LengthNotEqualError: If both lists are not of the same length.
        """
        self.__validate_other(other)
        if len(self.__data) != len(other.__data):
            raise LengthNotEqualError('Both Dynamic Lists must be of equal length.')

        # Subtract corresponding elements
        new_list = [self.__data[i] - other.__data[i] for i in range(len(self.__data))]
        return DynamicList.from_list(new_list, self.__allowed_type)

    def concat(self, other):
        """
        Concatenate two DynamicLists (like list + list in Python).

        Args:
            other (DynamicList): Another DynamicList to append.
        Returns:
            DynamicList: A new combined list.
        """
        self.__validate_other(other)
        new_list = DynamicList(self.__allowed_type)

        # Append elements from both lists
        new_list.extend(self.__data)
        new_list.extend(other.__data)
        return new_list

    def product(self):
        """
        Calculate the product of all numeric elements in the list.

        Returns:
            int | float: Product of all elements.
        Raises:
            WrongDataTypeError: If list contains non-numeric items.
        """
        self.__validate_contents_are_numeric()
        return reduce(lambda x, y: x * y, self.__data, 1)

    def __iadd__(self, other):
        """
        In-place addition operator (+=).
        Returns a new DynamicList as this class is immutable by design.
        """
        return self.__add__(other)

    def __mul__(self, scaler):
        """
        Repeat elements of the list (like Python list * n).

        Args:
            scaler (int): Number of repetitions.
        Returns:
            DynamicList: New list with repeated elements.
        Raises:
            TypeError: If scaler is not an integer.
        """
        if not isinstance(scaler, int):
            raise TypeError(f"Can only multiply DynamicList by an integer, not {type(scaler).__name__}.")

        # Repeat list elements
        new_data = self.__data * scaler
        return DynamicList.from_list(new_data, self.__allowed_type)

    def __imul__(self, scaler):
        """
        In-place multiplication (list *= n).
        Simply delegates to __mul__ since data is immutable.
        """
        return self.__mul__(scaler)

    def __rmul__(self, scaler):
        """
        Right-side multiplication (n * list).
        Allows reversed operand order.
        """
        return self.__mul__(scaler)

    def __bool__(self):
        """
        Boolean check for list emptiness.
        Returns True if list has items, False if empty.
        """
        return len(self.__data) != 0

    def min(self):
        """
        Return the smallest numeric element in the list.
        Raises error if list has non-numeric values.
        """
        self.__validate_contents_are_numeric()
        return min(self.__data)
        
    def max(self):
        """
        Return the largest numeric element in the list.
        Raises error if list has non-numeric values.
        """
        self.__validate_contents_are_numeric()
        return max(self.__data)

    def sum(self):
        """
        Calculate the sum of numeric elements in the list.

        Returns:
            int | float: Sum of all numeric elements.
        Raises:
            WrongDataTypeError: If list contains non-numeric types.
        """
        for i in self.__data:
            self.__validate_type(i, allowed_type=(int, float))
        return sum(self.__data)

    def map(self, func):
        """
        Apply a function to each element and return a new DynamicList.
        Similar to Python's built-in map(), but returns DynamicList instead of list.
        """
        new_list = [func(i) for i in self.__data]
        new_allowed_type = self.__allowed_type if not new_list else type(new_list[0])
        return DynamicList.from_list(new_list, new_allowed_type)
        
    def filter(self, func):
        """
        Filter elements based on a condition.
        Keeps items where func(item) is True.
        """
        new_list = [i for i in self.__data if func(i)]
        new_dlist = DynamicList.from_list(new_list, self.__allowed_type)
        return new_dlist
        
    def mean(self):
        """
        Return the arithmetic mean of numeric elements.
        """
        self.__validate_contents_are_numeric()
        return sum(self.__data) / len(self.__data)

    def median(self):
        """
        Return the median (middle value) of numeric elements.
        """
        self.__validate_contents_are_numeric()
        sorted_list = sorted(self.__data)
        n = len(sorted_list)
        mid = n // 2  
    
        if n % 2 != 0:
            return sorted_list[mid]
        else:
            return (sorted_list[mid - 1] + sorted_list[mid]) / 2

    def mode(self):
        """
        Return the most frequent element(s) in the list.
        Returns a single value if one mode exists, else a list of modes.
        """
        self.__validate_empty_list()
        counts = Counter(self.__data)
        max_count = max(counts.values())
        modes = [num for num, count in counts.items() if count == max_count]
        return modes[0] if len(modes) == 1 else modes
    
    def data_range(self):
        """
        Return the range of data (max - min).
        """
        self.__validate_empty_list()
        return self.max() - self.min()

    def variance(self):
        """
        Calculate variance of numeric elements.
        Measures how far data points spread from the mean.
        """
        self.__validate_contents_are_numeric()
        mean_val = self.mean()
        return sum((x - mean_val) ** 2 for x in self.__data) / (len(self.__data) - 1)
    
    def std(self):
        """
        Return the standard deviation.
        Square root of variance.
        """
        var = self.variance()
        return var ** 0.5

    def percentile(self, P):
        """
        Return the Pth percentile of numeric data.
        Uses linear interpolation between closest ranks.
        """
        self.__validate_contents_are_numeric()
    
        if not (0 <= P <= 100):
            raise UnknownValueError("Percentile must be between 0 and 100.")
    
        sorted_data = sorted(self.__data)
        n = len(sorted_data)
    
        # If only one element, return it directly
        if n == 1:
            return sorted_data[0]
    
        # Compute rank position
        rank = (P / 100) * (n - 1)
        lower_index = int(rank)
        upper_index = min(lower_index + 1, n - 1)
        fraction = rank - lower_index
    
        # Interpolate between two values
        lower_value = sorted_data[lower_index]
        upper_value = sorted_data[upper_index]
    
        return lower_value + fraction * (upper_value - lower_value)

    def cumulative_sum(self):
        """
        Return a new DynamicList containing cumulative sums of elements.
        Example: [1, 2, 3] -> [1, 3, 6]
        """
        cum_sum_list = []
        for index, i in enumerate(self.__data):
            # Ensure only numeric values are processed
            self.__validate_type(i, allowed_type=(int, float))
            # Sum elements up to current index
            cum_sum_list.append(sum(self.__data[:index + 1]))
        
        # Return as a new DynamicList
        cumsum_dlist = DynamicList.from_list(cum_sum_list, self.__allowed_type)
        return cumsum_dlist


    def normalize(self):
        """
        Return a normalized version of the list (values between 0 and 1).
        Formula: (x - min) / (max - min)
        """
        self.__validate_contents_are_numeric()
        scaled_list = []
        min_val, max_val = self.min(), self.max()

        # Avoid division by zero when all values are identical
        if max_val == min_val:
            raise ValueError("Cannot normalize a constant list (all values are equal).")

        # Scale each element to 0–1 range
        for value in self.__data:
            scaled_value = (value - min_val) / (max_val - min_val)
            scaled_list.append(scaled_value)

        # Return a new normalized DynamicList
        return DynamicList.from_list(scaled_list, allowed_type=(int, float))

    def describe(self):
        """
        Display and return basic statistical summary of the numeric data.
        Similar to pandas' describe(): shows count, mean, std, quartiles, etc.
        """
        # Ensure list is not empty and contains numeric values
        self.__validate_contents_are_numeric()
        self.__validate_empty_list()
    
        # Basic metrics
        n = len(self.__data)
        data_min = self.min()
        data_max = self.max()
        data_mean = self.mean()
        data_std = self.std()
        data_var = self.variance()
        q1 = self.percentile(25)
        q2 = self.percentile(50)  # Median
        q3 = self.percentile(75)
        data_range = self.data_range()
    
        # Prepare summary dictionary
        summary = {
            "count": n,
            "mean": round(data_mean, 3),
            "std": round(data_std, 3),
            "var": round(data_var, 3),
            "min": data_min,
            "25%": round(q1, 3),
            "50%": round(q2, 3),
            "75%": round(q3, 3),
            "max": data_max,
            "range": round(data_range, 3)
        }
    
        # Nicely formatted console output
        print(f"\nSummary Statistics ({self.__allowed_type})\n" + "-" * 35)
        for k, v in summary.items():
            print(f"{k:>7} : {v}")
        
        return summary
    

    def copy(self):
        """
        Return a shallow copy of the current DynamicList.
        """
        # Duplicate internal data and preserve allowed type
        copy_data = self.__data.copy()
        new_list = DynamicList.from_list(copy_data, self.__allowed_type)
        return new_list
        
    @classmethod
    def from_list(cls, regular_list, allowed_type=(int, float)):
        """
        Create a DynamicList instance from a regular Python list.
        """
        # Initialize new DynamicList and extend it with provided data
        new_dlist = cls(allowed_type)
        new_dlist.extend(regular_list)
        return new_dlist

    def to_list(self):
        """
        Convert DynamicList back to a regular Python list.
        """
        # Return a shallow copy of the internal list
        return self.__data.copy()
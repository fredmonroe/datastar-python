from enum import StrEnum
from typing import override, Any
import json


class EventType(StrEnum):
    MERGE_FRAGMENTS = "datastar-merge-fragments"
    REMOVE_FRAGMENTS = "datastar-remove-fragments"
    MERGE_SIGNALS = "datastar-merge-signals"
    REMOVE_SIGNALS = "datastar-remove-signals"
    EXECUTE_SCRIPT = "datastar-execute-script"


class FragmentMergeMode(StrEnum):
    MORPH = "morph"
    INNER = "inner"
    OUTER = "outer"
    PREPEND = "prepend"
    APPEND = "append"
    BEFORE = "before"
    AFTER = "after"
    DELETE = "delete"
    UPSERT_ATTRIBUTES = "upsert_attributes"


class DataStarEvent:
    def __init__(
        self,
        event_type: EventType,
        data: str,
        event_id: str | None = None,
        retry_duration: int = 1000,
    ):
        self.event_type: EventType = event_type
        self.data: str = data
        self.event_id: str | None = event_id
        self.retry_duration: int = retry_duration

    @override
    def __str__(self) -> str:
        message_lines = [f"event: {self.event_type.value}"]

        if self.event_id:
            message_lines.append(f"id: {self.event_id}")

        if self.retry_duration != 1000:
            message_lines.append(f"retry: {self.retry_duration}")

        for line in self.data.splitlines():
            message_lines.append(f"data: {line}")

        message_lines.append("\n")
        return "\n".join(message_lines)


class MergeFragmentsEvent(DataStarEvent):
    def __init__(
        self,
        data: str,
        *,
        selector: str | None = None,
        merge_mode: FragmentMergeMode = FragmentMergeMode.MORPH,
        settle_duration: int = 300,
        use_view_transition: bool = False,
        event_id: str | None = None,
        retry_duration: int = 1000,
    ):
        event_data: list[str] = []

        if selector:
            event_data.append(f"selector {selector}")

        if merge_mode != FragmentMergeMode.MORPH:
            event_data.append(f"mergeMode  {merge_mode.value}")

        if settle_duration != 300:
            event_data.append(f"settleDuration {settle_duration}")

        if use_view_transition:
            event_data.append(f"useViewTransition {str(use_view_transition).lower()}")

        for line in data.splitlines():
            event_data.append(f"fragments {line}")

        super().__init__(
            event_type=EventType.MERGE_FRAGMENTS,
            data="\n".join(event_data),
            event_id=event_id,
            retry_duration=retry_duration,
        )


class RemoveFragmentsEvent(DataStarEvent):
    def __init__(
        self,
        selector: str,
        *,
        settle_duration: int = 300,
        use_view_transition: bool = False,
        event_id: str | None = None,
        retry_duration: int = 1000,
    ):
        """
        Initializes a RemoveFragmentsEvent instance.

        Args:
            selector (str): CSS selector for the fragments to remove.
            settle_duration (int): Duration for settling animations (default: 300ms).
            use_view_transition (bool): Whether to use view transitions (default: False).
            event_id (str | None): Event ID for the message.
            retry_duration (int): Retry duration in milliseconds (default: 1000).
        """
        if not selector:
            raise ValueError("Selector must be provided for RemoveFragmentsEvent")

        event_data = [f"selector {selector}"]

        if settle_duration != 300:
            event_data.append(f"settleDuration {settle_duration}")

        if use_view_transition:
            event_data.append(f"useViewTransition {str(use_view_transition).lower()}")

        # Pass formatted data to the parent class
        super().__init__(
            event_type=EventType.REMOVE_FRAGMENTS,
            data="\n".join(event_data),
            event_id=event_id,
            retry_duration=retry_duration,
        )


class MergeSignalsEvent(DataStarEvent):
    def __init__(
        self,
        data: dict[str, Any],
        *,
        only_if_missing: bool = False,
        event_id: str | None = None,
        retry_duration: int = 1000,
    ):
        """
        Initializes a MergeSignalsEvent instance.

        Args:
            data (dict): The dictionary to send as signals, converted to JSON.
            only_if_missing (bool): Whether to send only if the data is missing in the store (default: False).
            event_id (str | None): Event ID for the message.
            retry_duration (int): Retry duration in milliseconds (default: 1000).
        """

        # Convert dictionary to JSON string
        json_data = json.dumps(data)

        event_data: list[str] = []

        # Add onlyIfMissing option
        if only_if_missing:
            event_data.append(f"onlyIfMissing {str(only_if_missing).lower()}")

        # Add the signals data
        for line in json_data.splitlines():
            event_data.append(f"signals {line}")

        # Pass formatted data to the parent class
        super().__init__(
            event_type=EventType.MERGE_SIGNALS,
            data="\n".join(event_data),
            event_id=event_id,
            retry_duration=retry_duration,
        )


class RemoveSignalsEvent(DataStarEvent):
    def __init__(
        self,
        paths: list[str],
        *,
        event_id: str | None = None,
        retry_duration: int = 1000,
    ):
        """
        Initializes a RemoveSignalsEvent instance.

        Args:
            paths (list[str]): A list of dot-delimited strings representing paths to signals.
            event_id (str | None): Event ID for the message.
            retry_duration (int): Retry duration in milliseconds (default: 1000).
        """

        # Join the paths with spaces
        paths_data = " ".join(paths)

        event_data = [f"paths {paths_data}"]

        # Pass formatted data to the parent class
        super().__init__(
            event_type=EventType.REMOVE_SIGNALS,
            data="\n".join(event_data),
            event_id=event_id,
            retry_duration=retry_duration,
        )


class ExecuteScriptEvent(DataStarEvent):
    def __init__(
        self,
        script: str,
        *,
        auto_remove: bool = True,
        attributes: list[str] | None = None,
        event_id: str | None = None,
        retry_duration: int = 1000,
    ):
        """
        Initializes an ExecuteScriptEvent instance.

        Args:
            script (str): The JavaScript code to execute in the browser.
            auto_remove (bool): Whether to remove the script after execution (default: True).
            attributes (list[str] | None): List of attributes in "key value" format.
            event_id (str | None): Event ID for the message.
            retry_duration (int): Retry duration in milliseconds (default: 1000).
        """
        if not script:
            raise ValueError("Script must be provided for ExecuteScriptEvent")

        event_data: list[str] = []

        # Handle autoRemove
        if not auto_remove:  # Only include if different from the default (True)
            event_data.append(f"autoRemove {str(auto_remove).lower()}")

        # Handle attributes
        if attributes:
            for attr in attributes:
                event_data.append(f"attributes {attr}")
        else:
            # Default attribute if not provided
            event_data.append("attributes type module")

        # Add script lines
        for line in script.splitlines():
            event_data.append(f"script {line}")

        # Pass formatted data to the parent class
        super().__init__(
            event_type=EventType.EXECUTE_SCRIPT,
            data="\n".join(event_data),
            event_id=event_id,
            retry_duration=retry_duration,
        )

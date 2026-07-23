from desktop.models.presentation import StandardDataset

class DatasetValidator:
    """
    Rule 337: Validates that models contain correctly formatted standard datasets
    before pushing them into PresentationModel and down to the frontend.
    """
    
    @staticmethod
    def validate(dataset: StandardDataset) -> bool:
        if dataset.dataset_type == "CHART":
            return DatasetValidator._validate_chart(dataset)
        elif dataset.dataset_type == "TIMELINE":
            return DatasetValidator._validate_timeline(dataset)
        elif dataset.dataset_type == "TABLE":
            return DatasetValidator._validate_table(dataset)
        # Add more schema validations here
        return True

    @staticmethod
    def _validate_chart(dataset) -> bool:
        # e.g., Ensure labels match series length
        if not hasattr(dataset, "labels") or not hasattr(dataset, "series"):
            return False
        return True

    @staticmethod
    def _validate_timeline(dataset) -> bool:
        if not hasattr(dataset, "events"):
            return False
        return True

    @staticmethod
    def _validate_table(dataset) -> bool:
        if not hasattr(dataset, "columns") or not hasattr(dataset, "rows"):
            return False
        return True

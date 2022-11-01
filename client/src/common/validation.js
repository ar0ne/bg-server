// Validation

const requiredField = value => {
    if (!value) {
        return (
            <div>
                This field is required!
            </div>
        )
    }
}

export default requiredField;
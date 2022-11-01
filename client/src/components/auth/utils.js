// Common

const required = value => {
    if (!value) {
        return (
            <div>
                This field is required!
            </div>
        )
    }
}

export default required;
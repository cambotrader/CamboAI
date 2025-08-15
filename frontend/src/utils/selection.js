// Fix for selection error
export const isSelection = () => {
    try {
        const selection = window.getSelection();
        return selection && selection.rangeCount > 0 && selection.toString().length > 0;
    } catch (error) {
        console.warn('Selection check failed:', error);
        return false;
    }
};

export const handleSelection = () => {
    try {
        if (!isSelection()) return;
        const selection = window.getSelection();
        const range = selection.getRangeAt(0);
        // Your selection handling code here
    } catch (error) {
        console.warn('Selection handling failed:', error);
    }
};

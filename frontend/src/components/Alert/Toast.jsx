import react, {useEffect} from 'react';

const Toast = ({ message, type,onClose}) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 3000);
        return () => clearTimeout(timer);
    }, [onClose]);

    const getBackgroundColor = () => {
        if (type == 'warnning') return '#f39c12';
        if (type == 'error') return '#e74c3c';
        return '#2ecc71';
        
    };

    return (
        <div className = "toast-message" style={{backgroundColor: getBackgroundColor()}}>
            <span>{type ==='warning' ? '⚠️' : type === 'error' ? '🚨' : '✅'}</span>
            <p>{message}</p>
            <button onClick={onClose}>X</button>
            </div>
    );
};

export default Toast;
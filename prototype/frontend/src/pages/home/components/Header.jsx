import { BusIcon, FlaskIcon } from '../../../components/icons';

export function Header({ isMocked }) {
    return (
        <header className="home__header">
            <h1 className="home__title">
                <BusIcon className="home__title-icon" />
                <span>Bus Radar</span>
            </h1>
            {isMocked && (
                <span className="home__mock-badge">
                    <FlaskIcon className="home__mock-icon" />
                    <span>Mock Location</span>
                </span>
            )}
        </header>
    );
}

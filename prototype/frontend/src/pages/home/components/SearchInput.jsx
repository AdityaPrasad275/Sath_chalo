export function SearchInput({ value, onChange, isSearching }) {
    return (
        <div className="home__search">
            <input
                type="text"
                className="home__search-input"
                placeholder="Search for a stop..."
                value={value}
                onChange={(e) => onChange(e.target.value)}
            />
            {isSearching && <span className="home__search-spinner" />}
        </div>
    );
}

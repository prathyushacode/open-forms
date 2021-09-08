import React from 'react';
import PropTypes from 'prop-types';
import {FormattedMessage, useIntl} from 'react-intl';
import jsonLogic from 'json-logic-js';

import {OPERATORS} from './constants';
import Select from '../../forms/Select';
import {NumberInput} from '../../forms/Inputs';
import {getTranslatedChoices} from '../../../../utils/i18n';


const Today = ({name, value, onChange}) => {
    const sign = value ? jsonLogic.get_operator(value) : '+';
    const years = value ? value[sign][1]['years'] : 0;

    const intl = useIntl();
    const operatorChoices = Object.entries(OPERATORS).filter(([operator]) => ['+', '-'].includes(operator));

    const onChangeSign = (event) => {
        const modifiedValue = {};
        modifiedValue[event.target.value] = [{today: []}, {years: years}];
        const fakeEvent = {target: {name: name, value: modifiedValue}};
        onChange(fakeEvent);
    };

    const onChangeYears = (event) => {
        const modifiedValue = {};
        modifiedValue[sign] = [{today: []}, {years: parseInt(event.target.value, 10)}];
        const fakeEvent = {target: {name: name, value: modifiedValue}};
        onChange(fakeEvent);
    };

    return (
        <div className="dsl-editor__node-group">
            <div className="dsl-editor__node">
                <Select
                    name="sign"
                    choices={getTranslatedChoices(intl, operatorChoices)}
                    onChange={onChangeSign}
                    value={sign}
                />
            </div>
            <div className="dsl-editor__node">
                <NumberInput
                    name="years"
                    value={years}
                    onChange={onChangeYears}
                    min={0}
                />
            </div>
            <div className="dsl-editor__node">
                <FormattedMessage description="Logic trigger number of years" defaultMessage="years" />
            </div>
        </div>
    );
};

Today.propTypes = {
    name: PropTypes.string.isRequired,
    value: PropTypes.object.isRequired,
    onChange: PropTypes.func.isRequired,
};

export default Today;

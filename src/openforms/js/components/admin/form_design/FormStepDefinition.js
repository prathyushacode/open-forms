/*
global URLify;
 */
import React from 'react';
import PropTypes from 'prop-types';
import {FormattedMessage} from 'react-intl';

import FormIOBuilder from '../../formio_builder/builder';
import {Checkbox, TextInput} from '../forms/Inputs';
import Field, {normalizeErrors} from '../forms/Field';
import FormRow from '../forms/FormRow';
import useDetectConfigurationChanged from './useDetectConfigurationChanged';
import ChangedFormDefinitionWarning from './ChangedFormDefinitionWarning';
import PluginWarning from './PluginWarning';
import AuthenticationWarning from './AuthenticationWarning';
import useDetectSimpleLogicErrors from './useDetectSimpleLogicErrors';
import LogicWarning from './LogicWarning';

const emptyConfiguration = {
    display: 'form',
};


/**
 * Load the form builder for a given form definition.
 *
 * Note that the underlying FormIOBuilder creates a ref from the configuration. The
 * actual builder state is maintained by FormioJS itself and we are not driven that
 * state via props - only the initial state!
 *
 * We can solely use the onChange handler to keep track of our own 'application'
 * state to eventually persist the data. This goes against React's best practices,
 * but we're fighting the library at this point.
 *
 */
const FormStepDefinition = ({ url='', name='', internalName='', slug='', previousText='', saveText='', nextText='',
                                loginRequired=false, isReusable=false, configuration=emptyConfiguration,
                                onChange, onComponentMutated, onFieldChange, onLiteralFieldChange, errors,
                                ...props }) => {

    const setSlug = () => {
        // do nothing if there's already a slug set
        if (slug) return;

        // sort-of taken from Django's jquery prepopulate module
        const newSlug = URLify(name, 100, false);
        onFieldChange({
            target: {
                name: 'slug',
                value: newSlug,
            }
        });
    };

    const { changed, affectedForms } = useDetectConfigurationChanged(url, configuration);
    const { warnings } = useDetectSimpleLogicErrors(configuration);

    return (
        <>
            <ChangedFormDefinitionWarning changed={changed} affectedForms={affectedForms} />
            <PluginWarning loginRequired={loginRequired} configuration={configuration}/>
            <AuthenticationWarning loginRequired={loginRequired} configuration={configuration}/>
            <LogicWarning warnings={warnings}/>

            <fieldset className="module aligned">
                <h2>
                    <FormattedMessage description="Form definition module title" defaultMessage="Form definition" />
                </h2>

                <FormRow>
                    <Field
                        name="name"
                        label={<FormattedMessage defaultMessage="Step name" description="Form step name label" />}
                        helpText={<FormattedMessage
                            defaultMessage="Name of the form definition used in this form step"
                            description="Form step name field help text" />}
                        required
                        fieldBox
                    >
                        <TextInput value={name} onChange={onFieldChange} onBlur={setSlug} />
                    </Field>
                    <Field
                        name="internalName"
                        label={<FormattedMessage defaultMessage="Internal step name" description="Form step internal name label" />}
                        helpText={<FormattedMessage
                            defaultMessage="Internal name of the form definition used in this form step"
                            description="Form step internal name field help text" />}
                        fieldBox
                    >
                        <TextInput value={internalName} onChange={onFieldChange} />
                    </Field>
                    <Field
                        name="slug"
                        label={<FormattedMessage defaultMessage="Step slug" description="Form step slug label" />}
                        helpText={<FormattedMessage
                            defaultMessage="Slug of the form definition used in this form step"
                            description="Form step slug field help text" />}
                        required
                        fieldBox
                    >
                        <TextInput value={slug} onChange={onFieldChange}/>
                    </Field>
                </FormRow>
                <FormRow>
                    <Field
                        name="previousText"
                        label={<FormattedMessage defaultMessage="Previous text" description="Form step previous text label" />}
                        helpText={<FormattedMessage
                            defaultMessage="The text that will be displayed in the form step to go to the previous step. Leave blank to get value from global configuration."
                            description="Form step previous text field help text" />}
                        fieldBox
                    >
                        <TextInput value={previousText} onChange={onLiteralFieldChange} maxLength="50"/>
                    </Field>
                    <Field
                        name="saveText"
                        label={<FormattedMessage defaultMessage="Save text" description="Form step save text label" />}
                        helpText={<FormattedMessage
                            defaultMessage="The text that will be displayed in the form step to save the current information. Leave blank to get value from global configuration."
                            description="Form step save text field help text" />}
                        fieldBox
                    >
                        <TextInput value={saveText} onChange={onLiteralFieldChange} maxLength="50"/>
                    </Field>
                    <Field
                        name="nextText"
                        label={<FormattedMessage defaultMessage="Next text" description="Form step next text label" />}
                        helpText={<FormattedMessage
                            defaultMessage="The text that will be displayed in the form step to go to the next step. Leave blank to get value from global configuration."
                            description="Form step next text field help text" />}
                        fieldBox
                    >
                        <TextInput value={nextText} onChange={onLiteralFieldChange} maxLength="50"/>
                    </Field>
                </FormRow>
                <FormRow>
                    <Checkbox
                        label={<FormattedMessage defaultMessage="Login required?" description="Form step login required label" />}
                        name="loginRequired"
                        checked={loginRequired}
                        onChange={(e) => onFieldChange({target: {name: 'loginRequired', value: !loginRequired}})}
                    />
                </FormRow>
                <FormRow>
                    <Checkbox
                        label={<FormattedMessage defaultMessage="Is reusable?" description="Form step is reusable label" />}
                        name="isReusable"
                        checked={isReusable}
                        onChange={(e) => onFieldChange({target: {name: 'isReusable', value: !isReusable}})}
                    />
                </FormRow>
            </fieldset>

            <h2>Velden</h2>

            <div className="formio-builder-wrapper">
                <ConfigurationErrors errors={errors} />
                <FormIOBuilder
                    configuration={configuration}
                    onChange={onChange}
                    onComponentMutated={onComponentMutated}
                    {...props}
                />
            </div>
        </>
    );
};

FormStepDefinition.propTypes = {
    configuration: PropTypes.object,
    name: PropTypes.string,
    internalName: PropTypes.string,
    url: PropTypes.string,
    slug: PropTypes.string,
    previousText: PropTypes.string,
    saveText: PropTypes.string,
    nextText: PropTypes.string,
    loginRequired: PropTypes.bool,
    isReusable: PropTypes.bool,
    onChange: PropTypes.func.isRequired,
    onComponentMutated: PropTypes.func.isRequired,
    onFieldChange: PropTypes.func.isRequired,
    onLiteralFieldChange: PropTypes.func.isRequired,
    errors: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
};


const ConfigurationErrors = ({ errors=[] }) => {
    const configurationErrors = errors.filter(([name, err]) => name === 'configuration');
    const [hasConfigurationErrors, formattedConfigurationErrors] = normalizeErrors(configurationErrors);

    if (!hasConfigurationErrors) return null;
    return (
        <ul className="messagelist">
            {
                formattedConfigurationErrors.map((err, index) => (
                    <li key={index} className="error">{err}</li>
                ))
            }
        </ul>
    );
};

ConfigurationErrors.propTypes = {
    errors: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
};


export default FormStepDefinition;

# xml2pyton

Takes XML input and converts it to a dict. The output can be optimized by removing unnecessary nesting or ensuring lists
in ambiguous cases, so you can easily handle it afterwards, eg in [validataclass](https://pypi.org/project/validataclass/).

## Usage

Without the optional arguments, this:

```xml
<Envelope>
    <Header>
        <Security>
            <UsernameToken>
                <Username>Ghost</Username>
                <Password>Boo</Password>
            </UsernameToken>
        </Security>
    </Header>
    <Body>
        <Content>
            <ContentText>
                <Text>some text</Text>
            </ContentText>
        </Content>
    </Body>
</Envelope>
```

... will be converted to this:

```
{
    'Envelope': {
        'Body': {
            'Content': {
                'ContentText': {
                    'Text': 'some text',
                }
            }
        },
        'Header': {
            'Security': {
                'UsernameToken': {
                    'Password': 'Boo',
                    'Username': 'Ghost',
                }
            }
        }
    }
}
```


### Parameter `ensure_array_keys`

The `ensure_array_keys` list can be provided to specify for which keys in which tags, the values
should always be interpreted as items of a list. In case there is only one child item, they would otherwise
not be recognizable as a list in the XML.

With `ensure_array_keys=[('Envelope', 'Header'), ('Content', 'ContentText')]`,
the example above would be converted to this, interpreting the values of the given keys as lists:

```
{
    'Envelope': {
        'Body': {
            'Content': {
                'ContentText': [
                    {'Text': 'some text'},
                ]
            }
        },
        'Header': [
            {
                'Security': {
                    'UsernameToken': {
                        'Password': 'Boo',
                        'Username': 'Ghost'
                    }
                }
            },
        ]
    }
}
```


### Parameter `remote_type_tags`

The `remote_type_tags` list can be provided to specify which tags should be interpreted as names of types,
e.g. enums, which don't need to be preserved as keys in the output dict.

For example, this:

```xml
<status>
    <ChargePointStatusType>Operative</ChargePointStatusType>
</status>
```

would usually be converted to this:

```
{
    'status': {
        'ChargePointStatusType': 'Operative',
    }
}
```

But if `ChargePointStatusType` is given in the `remote_type_tags` list,  it will be converted to this
simpler version:

```
{
    'status': 'Operative'
}
```

Which could then be parsed into an enum value if necessary.

Another use case for `remote_type_tags` would be to skip a level in the nested data
that has only one field (!) of which the name does also not need to be preserved as a key.

With `remote_type_tags=['Envelope', 'Content', 'ContentText', 'Text', 'Security', 'UsernameToken']`,
the first example above can become as compact as this:

```
{
    'Body': 'some text',
    'Header': {
        'Password': 'Boo',
        'Username': 'Ghost',
    }
}
```

The `Body`, `Header`, `Username` and `Password` keys cannot be removed
because there are multiple keys on their levels.


### Parameter: `conditional_remote_type_tags`

The `conditional_remote_type_tags` list can be used to skip a tag depending on the name of its parent tag.
This is most useful for tags where the field name and the type name are the same,
but only one of them should be skipped, for example:

```xml
<resultCode>
    <resultCode>ok</resultCode>
</resultCode>
```

can be parsed into a non-nested field named 'resultCode' with the content 'ok'
by giving `conditional_remote_type_tags=[('resultCode', 'resultCode')]`.

The 'ignore_attributes' list can be given to avoid parsing attributes with a certain name.
This is useful if a tag could either have a simple string value as a child, or be self-closing -
and the self-closing version should be interpreted as if the tag's value is null
(because there might be attributes that say this, but in a weirdly complicated way).

For example, a tag like this is 'null' in terms of practical use:

```
<resultDescription xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>
```

But it would normally be parsed as a dictionary here:

```
'resultDescription': {'{http://www.w3.org/2001/XMLSchema-instance}nil': 'true'}
```

And if we were to just skip the attribute by adding it to `remote_type_tags`, we would get this instead:

```
'resultDescription': 'true'
```

Which would be very misleading. So to parse this tag into a useful value for an 'Optional[str]' type field,
the ignore_attributes list can be used.
With ignore_attributes=['{http://www.w3.org/2001/XMLSchema-instance}nil'], we get a result that fits the type:

```
'resultDescription': None
```


## Licence

This library is under MIT licence. Please look at `LICENCE.txt` for details.

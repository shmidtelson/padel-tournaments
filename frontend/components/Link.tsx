'use client';

import NextLink from 'next/link';

type Props = React.ComponentProps<typeof NextLink>;

export function Link(props: Props) {
  return <NextLink {...props} />;
}

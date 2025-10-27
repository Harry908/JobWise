import 'package:flutter/material.dart';

class TagInput extends StatefulWidget {
  final List<String> initialTags;
  final ValueChanged<List<String>> onTagsChanged;
  final String labelText;
  final String hintText;
  final String? helperText;
  final bool enabled;
  final int? maxTags;

  const TagInput({
    Key? key,
    required this.initialTags,
    required this.onTagsChanged,
    required this.labelText,
    this.hintText = '',
    this.helperText,
    this.enabled = true,
    this.maxTags,
  }) : super(key: key);

  @override
  State<TagInput> createState() => _TagInputState();
}

class _TagInputState extends State<TagInput> {
  late List<String> _tags;
  final TextEditingController _controller = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _tags = List.from(widget.initialTags);
  }

  @override
  void didUpdateWidget(TagInput oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.initialTags != widget.initialTags) {
      _tags = List.from(widget.initialTags);
    }
  }

  void _addTag(String tag) {
    final trimmedTag = tag.trim();
    if (trimmedTag.isNotEmpty &&
        !_tags.contains(trimmedTag) &&
        (widget.maxTags == null || _tags.length < widget.maxTags!)) {
      setState(() {
        _tags.add(trimmedTag);
      });
      _controller.clear();
      widget.onTagsChanged(_tags);
    }
  }

  void _removeTag(String tag) {
    setState(() {
      _tags.remove(tag);
    });
    widget.onTagsChanged(_tags);
  }

  void _onSubmitted(String value) {
    _addTag(value);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.labelText,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 8),
        if (_tags.isNotEmpty) ...[
          Wrap(
            spacing: 8,
            runSpacing: 4,
            children: _tags.map((tag) {
              return Chip(
                label: Text(
                  tag,
                  style: theme.textTheme.bodyMedium,
                ),
                deleteIcon: Icon(
                  Icons.close,
                  size: 18,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                onDeleted: widget.enabled ? () => _removeTag(tag) : null,
                backgroundColor: theme.colorScheme.surfaceContainerHighest,
                side: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.3),
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 12),
        ],
        TextField(
          controller: _controller,
          focusNode: _focusNode,
          enabled: widget.enabled && (widget.maxTags == null || _tags.length < widget.maxTags!),
          decoration: InputDecoration(
            hintText: widget.hintText,
            helperText: widget.helperText,
            suffixIcon: IconButton(
              icon: Icon(
                Icons.add,
                color: theme.colorScheme.primary,
              ),
              onPressed: widget.enabled && (widget.maxTags == null || _tags.length < widget.maxTags!)
                  ? () => _addTag(_controller.text)
                  : null,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: theme.colorScheme.outline,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: theme.colorScheme.outline,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide(
                color: theme.colorScheme.primary,
                width: 2,
              ),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 14,
            ),
          ),
          onSubmitted: _onSubmitted,
          textInputAction: TextInputAction.done,
          style: theme.textTheme.bodyLarge,
        ),
        if (widget.maxTags != null) ...[
          const SizedBox(height: 4),
          Text(
            '${_tags.length}/${widget.maxTags} skills added',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }
}